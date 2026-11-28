"""渠道指纹检查：同一请求发到两个渠道，比较 prompt_tokens、首 20 个 token 与 logprobs（docs/修订实验方案.md 第十一节）。

  # 每个渠道各跑一次（Key 只从环境变量读，输出中不含 Key 与地址）
  python src/channel_fingerprint.py probe --name ds_ark --base-env FP_BASE --key-env FP_KEY \
      --model deepseek-v4-1-flash-261017 --out results/fingerprint/ds_ark.json
  # 比较两个渠道
  python src/channel_fingerprint.py compare results/fingerprint/ds_ark.json results/fingerprint/ds_dmx.json

请求与实验第 0 轮相同（system + ClassEval direct 首条提示），另加 max_tokens、logprobs；不改动实验代码。
"""
import argparse
import json
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prompts as P  # noqa: E402
from data import load_classeval  # noqa: E402

N_PROMPTS, REPS, MAX_TOKENS, TOP_K = 10, 2, 20, 5
LP_TOL, AGREE_MARGIN = 0.05, 0.2          # 判定阈值，见方案第十一节


def task_ids() -> list[int]:
    """固定取 ClassEval 题号排序后的前 N_PROMPTS 道题。"""
    return sorted(load_classeval())[:N_PROMPTS]


def messages_for(item: dict) -> list[dict]:
    return [{"role": "system", "content": P.SYSTEM},
            {"role": "user", "content": P.DIRECT.format(question=item["prompt"])}]


def one_call(client, model: str, msgs: list[dict], temperature: float, max_tokens: int = MAX_TOKENS) -> dict:
    """max_tokens = 0 表示不设上限（推理模型在 20 个 token 内只做内部推理、返回空 choices）。"""
    kw = dict(model=model, messages=msgs, temperature=temperature, **({"max_tokens": max_tokens} if max_tokens else {}))
    try:
        try:
            resp = client.chat.completions.create(**kw, logprobs=True, top_logprobs=TOP_K)
        except Exception:                      # 渠道不接受 logprobs 时（有的只报笼统的 400）退回不带 logprobs；再失败才记为错误
            resp = client.chat.completions.create(**kw)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:300]}"}
    if not getattr(resp, "choices", None):
        return {"error": f"empty choices: {str(resp)[:300]}"}
    ch, u = resp.choices[0], resp.usage
    lp = getattr(ch, "logprobs", None)
    toks = ([{"t": t.token, "lp": t.logprob, "top": [[x.token, x.logprob] for x in (t.top_logprobs or [])]}
             for t in lp.content] if lp is not None and getattr(lp, "content", None) else None)
    return {"served_model": resp.model, "system_fingerprint": getattr(resp, "system_fingerprint", None),
            "prompt_tokens": getattr(u, "prompt_tokens", None),
            "completion_tokens": getattr(u, "completion_tokens", None),
            "content": ch.message.content, "tokens": toks}


def cmd_probe(a) -> None:
    from openai import OpenAI
    client = OpenAI(base_url=os.environ[a.base_env], api_key=os.environ[a.key_env], timeout=120, max_retries=2)
    items = load_classeval()
    calls = []
    for i in task_ids():
        for rep in range(REPS):
            c = {"id": i, "rep": rep, **one_call(client, a.model, messages_for(items[i]), a.temperature, a.max_tokens)}
            calls.append(c)
            print(i, rep, c.get("served_model"), c.get("prompt_tokens"), "logprobs" if c.get("tokens") else "-",
                  c.get("error", ""), flush=True)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"name": a.name, "model": a.model, "temperature": a.temperature, "max_tokens": a.max_tokens, "calls": calls},
                  f, ensure_ascii=False, indent=1)
    print("写入", a.out)


def token_seq(c: dict) -> list[str] | None:
    return [t["t"] for t in c["tokens"]] if c.get("tokens") else None


def pair_stats(x: dict, y: dict) -> dict:
    """两次调用：返回的 token 序列是否完全相同、公共前缀长度、公共前缀上所选 token 的 |logprob 差|。"""
    sx, sy = token_seq(x), token_seq(y)
    if sx is None or sy is None:
        return {"identical": (x.get("content") or "") == (y.get("content") or ""), "prefix": None, "lp_diffs": []}
    k = 0
    while k < min(len(sx), len(sy)) and sx[k] == sy[k]:
        k += 1
    return {"identical": sx == sy, "prefix": k,
            "lp_diffs": [abs(x["tokens"][j]["lp"] - y["tokens"][j]["lp"]) for j in range(k)]}


def summarize(pairs: list[dict]) -> dict:
    diffs = [d for p in pairs for d in p["lp_diffs"]]
    return {"n": len(pairs),
            "identical_rate": round(sum(p["identical"] for p in pairs) / len(pairs), 3) if pairs else None,
            "median_lp_diff": round(st.median(diffs), 4) if diffs else None}


def compare(a: dict, b: dict) -> dict:
    """判定（方案第十一节）：C1 每题 prompt_tokens 相同；C2 两边都有 logprobs 时，跨渠道公共前缀上 |logprob 差| 的中位数 < LP_TOL；
    C3 temperature 为 0 时，跨渠道「返回序列完全相同」的比例不低于两个渠道各自两次之间该比例的较小值减 AGREE_MARGIN。
    C1 必须满足；C2、C3 不适用时记 None，不计入不一致。"""
    ca = {(c["id"], c["rep"]): c for c in a["calls"] if "error" not in c}
    cb = {(c["id"], c["rep"]): c for c in b["calls"] if "error" not in c}
    ids = sorted({i for i, _ in ca} & {i for i, _ in cb})
    pt = {i: (ca.get((i, 0), {}).get("prompt_tokens"), cb.get((i, 0), {}).get("prompt_tokens")) for i in ids}
    within = {n: summarize([pair_stats(c[(i, 0)], c[(i, 1)]) for i in ids if (i, 0) in c and (i, 1) in c])
              for n, c in ((a["name"], ca), (b["name"], cb))}
    cross = summarize([pair_stats(ca[(i, r)], cb[(i, r)]) for i in ids for r in range(REPS)
                       if (i, r) in ca and (i, r) in cb])
    has_lp = bool(ca) and bool(cb) and all(c.get("tokens") for c in [*ca.values(), *cb.values()])
    greedy = a["temperature"] == 0 and b["temperature"] == 0
    c1 = len(ids) == N_PROMPTS and all(x is not None and x == y for x, y in pt.values())
    c2 = (cross["median_lp_diff"] is not None and cross["median_lp_diff"] < LP_TOL) if has_lp else None
    w = [v["identical_rate"] for v in within.values() if v["identical_rate"] is not None]
    c3 = (cross["identical_rate"] >= min(w) - AGREE_MARGIN
          if greedy and w and cross["identical_rate"] is not None else None)
    checks = {"C1_prompt_tokens_equal": c1, "C2_logprob_close": c2, "C3_cross_agreement": c3}
    pairs_w = {n: [(c[(i, 0)], c[(i, 1)]) for i in ids if (i, 0) in c and (i, 1) in c]
               for n, c in ((a["name"], ca), (b["name"], cb))}
    pairs_x = [(ca[(i, r)], cb[(i, r)]) for i in ids for r in range(REPS) if (i, r) in ca and (i, r) in cb]
    def comp(c: dict) -> float | None:
        v = [x["completion_tokens"] for x in c.values() if x.get("completion_tokens")]
        return st.median(v) if v else None
    descriptive = {                         # 事后补充的描述性指标（方案第十一节补记），不参与判定
        "top5": ({n: top5_stats(p) for n, p in pairs_w.items()} | {"cross": top5_stats(pairs_x)}) if has_lp else None,
        "median_completion_tokens": {a["name"]: comp(ca), b["name"]: comp(cb)}}
    return {"a": a["name"], "b": b["name"], "n_prompts": len(ids), "prompt_tokens": pt,
            "served": {a["name"]: sorted({str(c["served_model"]) for c in ca.values()}),
                       b["name"]: sorted({str(c["served_model"]) for c in cb.values()})},
            "within": within, "cross": cross, "has_logprobs": has_lp, "checks": checks,
            "verdict": "一致" if c1 and c2 is not False and c3 is not False else "不一致",
            "descriptive": descriptive}


def top5_stats(pairs: list[tuple]) -> dict:
    """在上下文相同的位置（公共前缀及分叉位）比较两次调用的 top-5 分布：重合率、top-1 一致率、共有候选的 |logprob 差|。"""
    diffs, overlap, top1 = [], [], []
    for x, y in pairs:
        k = pair_stats(x, y)["prefix"]
        for j in range(min(k + 1, len(x["tokens"]), len(y["tokens"]))):
            px, py = dict(map(tuple, x["tokens"][j]["top"])), dict(map(tuple, y["tokens"][j]["top"]))
            if not px or not py:
                continue
            common = set(px) & set(py)
            overlap.append(len(common) / TOP_K)
            diffs += [abs(px[t] - py[t]) for t in common]
            top1.append(max(px, key=px.get) == max(py, key=py.get))
    if not overlap:
        return {"positions": 0}
    return {"positions": len(overlap), "top5_overlap": round(st.mean(overlap), 3), "top1_agree": round(st.mean(top1), 3),
            "median_lp_diff": round(st.median(diffs), 4), "p90_lp_diff": round(sorted(diffs)[int(0.9 * len(diffs))], 4)}


def cmd_compare(a) -> None:
    with open(a.a, encoding="utf-8") as f, open(a.b, encoding="utf-8") as g:
        res = compare(json.load(f), json.load(g))
    text = json.dumps(res, ensure_ascii=False, indent=1, default=str)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe")
    p.add_argument("--name", required=True)
    p.add_argument("--base-env", required=True)
    p.add_argument("--key-env", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int, default=MAX_TOKENS)
    p.add_argument("--out", required=True)
    c = sub.add_parser("compare")
    c.add_argument("a")
    c.add_argument("b")
    c.add_argument("--out")
    args = ap.parse_args()
    cmd_probe(args) if args.cmd == "probe" else cmd_compare(args)
