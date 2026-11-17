"""独立重采样基线（Pass@k）：同一预算（k 次独立生成）下与多轮编译反馈修复对比。

用法：
  python src/sample_passk.py --model doubao-seed-2-0-mini-260428 --prompt direct -k 6 --temp 0.8 -j 6 -o results/exp/doubao_mini_direct_pass6.jsonl
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prompts as P  # noqa: E402
from data import load_humaneval, load_syntax_rule, read_jsonl, write_jsonl  # noqa: E402
from llm import chat, extract_code, strip_main  # noqa: E402
from runner import compile_and_run  # noqa: E402

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, **k):
        return x


def pass_at_k(n: int, c: int, k: int) -> float:
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def sample_one(item: dict, args, syntax_rule: str) -> dict:
    q = P.DIRECT.format(question=item["prompt"]) if args.prompt == "direct" else P.SYNTAX.format(
        syntax_rule=syntax_rule, question=item["prompt"]
    )
    msgs = [{"role": "system", "content": P.SYSTEM}, {"role": "user", "content": q}]
    samples, usage_total = [], {"prompt_tokens": 0, "completion_tokens": 0}
    for i in range(args.k):
        reply, u = chat(msgs, model=args.model, temperature=args.temp)
        for k in usage_total:
            usage_total[k] += u[k]
        code = strip_main(extract_code(reply)) if args.strip_main else extract_code(reply)
        res = compile_and_run(code + "\n" + item["test"])
        samples.append({"sample_idx": i, "passed": res.passed, "failure_kind": res.failure_kind})
    c = sum(1 for s in samples if s["passed"])
    return {"id": item["id"], "n_samples": args.k, "n_passed": c,
            "passed": c > 0, "usage": usage_total, "samples": samples}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--prompt", choices=["direct", "syntax"], default="direct")
    ap.add_argument("-k", type=int, default=6)
    ap.add_argument("--temp", type=float, default=0.8)
    ap.add_argument("--strip-main", action="store_true", default=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("-j", "--workers", type=int, default=6)
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    ds = load_humaneval()
    syntax_rule = load_syntax_rule() if args.prompt == "syntax" else ""
    items = list(ds.values())[: args.limit] if args.limit else list(ds.values())

    done: dict[int, dict] = {}
    if os.path.exists(args.output):
        for r in read_jsonl(args.output):
            if "error" not in r:
                done[int(r["id"])] = r
        print(f"[resume] 已完成 {len(done)}/{len(items)} 题，跳过")

    todo = [it for it in items if it["id"] not in done]
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    lock = threading.Lock()

    def run(it):
        try:
            return sample_one(it, args, syntax_rule)
        except Exception as e:
            return {"id": it["id"], "passed": False, "error": repr(e), "samples": []}

    with open(args.output, "a", encoding="utf-8") as fout, ThreadPoolExecutor(args.workers) as ex:
        futs = [ex.submit(run, it) for it in todo]
        for fut in tqdm(as_completed(futs), total=len(futs)):
            row = fut.result()
            with lock:
                fout.write(json.dumps(row, ensure_ascii=False) + "\n")
                fout.flush()
            done[int(row["id"])] = row

    rows = [done[it["id"]] for it in items if it["id"] in done]
    rows.sort(key=lambda r: r["id"])
    write_jsonl(args.output, rows)

    n = len(rows)
    unbiased = [round(100 * sum(pass_at_k(args.k, r.get("n_passed", 0), kk) for r in rows) / n, 2)
                for kk in range(1, args.k + 1)]
    cum_seq = [round(100 * sum(1 for r in rows if any(s["passed"] for s in r.get("samples", [])[:kk])) / n, 2)
               for kk in range(1, args.k + 1)]
    summary = {
        "config": vars(args), "n": n,
        "pass@k_unbiased": unbiased,
        "pass@k_sequential": cum_seq,
        "total_prompt_tokens": sum(r.get("usage", {}).get("prompt_tokens", 0) for r in rows),
        "total_completion_tokens": sum(r.get("usage", {}).get("completion_tokens", 0) for r in rows),
        "errors": sum(1 for r in rows if "error" in r),
    }
    with open(args.output.replace(".jsonl", "") + ".summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
