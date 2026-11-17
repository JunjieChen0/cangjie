"""零成本补充统计（只读已有实验数据，不调用任何大模型 API）。

1. Test 半区检验：在 seed=42 划分的 Test 82 题上做 hint vs raw；规则在 Dev/Test 公开失败样本中的命中次数
2. 多重比较：主比较单独检验，其余 R5 成对比较做 Holm 校正
3. 成本：按官方单价折算人民币；每题成本、每个通过题成本；pass@k 与多轮修复的 token-通过率曲线
4. 口径：第 0 轮失败类型分布（timeout 单列）；反馈 3000 字符截断率（--recompile 时重新编译确认）

用法：
  python src/extra_stats.py               # 全部统计（截断率读取缓存，没有缓存则只给下界）
  python src/extra_stats.py --recompile   # 额外重新编译被截断存储的反馈，确认真实长度（约 10 分钟）
输出：results/stats/extra_stats.json、results/stats/extra_stats.md
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import random
import re
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import load_exp, mcnemar_p, round_passed  # noqa: E402
from data import BENCH_DIR, ROOT, load_classeval, load_humaneval  # noqa: E402
from repair_hints import RULES  # noqa: E402
from split_eval import get_split  # noqa: E402

EXP = os.path.join(ROOT, "results", "exp")
ABL = os.path.join(ROOT, "results", "ablation")
REEVAL = os.path.join(ROOT, "results", "reeval")
OUT = os.path.join(ROOT, "results", "stats")

# 火山方舟「模型价格」页，在线推理（常规），元 / 百万 tokens：(输入, 输出)。快照日期 2026-11-17。
# 实验实际通过 Coding Plan 订阅调用，这里是按量计费单价的等价折算；未计缓存命中折扣（偏高估计）。
PRICE_DATE = "2026-11-17"
PRICES = {
    "doubao": {"list": (0.2, 2.0)},                      # doubao-seed-2.0-mini，输入长度 [0, 32K]
    "ds_v41f": {"offpeak": (1.0, 4.0), "peak": (2.0, 8.0)},  # deepseek-v4-1-flash，空闲 / 高峰
    "kimik31p": {"list": (13.0, 68.0)},                   # kimi-k3.1-pro
}
STORED_FEEDBACK_CAP = 1500   # repair.py 写入 history 时的截断长度
PROMPT_FEEDBACK_CAP = 3000   # runner.RunResult.feedback 喂给模型时的截断长度
PRIMARY = ("doubao_mini_direct", "hint", "raw")


# ---------------------------------------------------------------- 通用工具
def holm(pvals: list[float]) -> list[float]:
    """Holm–Bonferroni 校正后的 p 值（保持输入顺序，单调且不超过 1）。"""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj, running = [0.0] * m, 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[i]))
        adj[i] = running
    return adj


def bootstrap_ci(diffs: list[float], n_boot: int = 10000, seed: int = 0) -> tuple[float, float, float]:
    """按题目重抽样，返回 (均值, 2.5% 分位, 97.5% 分位)，单位为百分点。"""
    rng = random.Random(seed)
    n = len(diffs)
    boots = sorted(100 * sum(rng.choice(diffs) for _ in range(n)) / n for _ in range(n_boot))
    return 100 * sum(diffs) / n, boots[int(0.025 * n_boot)], boots[min(int(0.975 * n_boot), n_boot - 1)]


def pass_at_k(n: int, c: int, k: int) -> float:
    """无偏 pass@k 估计（Chen et al., 2021）。"""
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def model_key(name: str) -> str:
    return next(k for k in PRICES if name.startswith(k))


def cost_yuan(prompt_tokens: int, completion_tokens: int, model: str) -> dict[str, float]:
    return {tier: round((prompt_tokens * pin + completion_tokens * pout) / 1e6, 3)
            for tier, (pin, pout) in PRICES[model].items()}


def calls_until(row: dict, k: int, has_init: bool) -> int:
    """在第 k 轮截止时这道题调用了几次模型（第 0 轮生成 + 修复次数）。"""
    executed = len(row.get("history", [])) - 1     # 实际修复次数
    return (0 if has_init else 1) + min(k, executed)


def load(path: str) -> dict[str, dict]:
    return {str(r["id"]): r for r in load_exp(path)}


def rate(rows: dict[str, dict], ids, k: int = 5) -> float:
    ids = list(ids)
    return 100 * sum(round_passed(rows[i], k) for i in ids) / len(ids)


def mcnemar(a: dict[str, dict], b: dict[str, dict], ids, k: int = 5) -> tuple[int, int, float]:
    ids = sorted(ids)
    return mcnemar_p([dict(a[i], id=i) for i in ids], [dict(b[i], id=i) for i in ids], k)


# ---------------------------------------------------------------- 数据装载
def load_all() -> dict[str, dict[str, dict]]:
    data = {}
    for p in glob.glob(os.path.join(EXP, "*_r5.jsonl")):
        name = os.path.basename(p)[:-6]
        if "_ce_" in name:
            continue  # ClassEval 用全部测试口径，见下
        data[name] = load(p)
    for p in glob.glob(os.path.join(REEVAL, "*.alltests.jsonl")):
        name = os.path.basename(p).replace(".alltests.jsonl", "")
        data[name] = {str(r["id"]): {"passed": r["passed_all"], "rounds_used": r["rounds_used"]}
                      for r in load_exp(p)}
    for p in glob.glob(os.path.join(ABL, "*.jsonl")):
        name = os.path.basename(p)[:-6]
        if name not in ("doubao_mini_r0_init", "doubao_mini_direct_pass6"):
            data[name] = load(p)
    return data


def load_raw() -> dict[str, dict[str, dict]]:
    """含 history 的修复实验原始记录（含 ClassEval），用于口径统计。"""
    paths = glob.glob(os.path.join(EXP, "*_r5.jsonl")) + glob.glob(os.path.join(ABL, "*_r5.jsonl")) \
        + glob.glob(os.path.join(ABL, "*_rep[0-9].jsonl"))
    return {os.path.basename(p)[:-6]: load(p) for p in paths}


# ---------------------------------------------------------------- 1. Test 半区
def rule_hits_by_split(dev: set[int], test: set[int]) -> list[dict]:
    paths = glob.glob(os.path.join(BENCH_DIR, "Results", "**", "*HumanEval*.records.jsonl"), recursive=True)
    hits = {"dev": Counter(), "test": Counter()}
    for p in paths:
        for r in load_exp(p):
            if r.get("passed"):
                continue
            half = "dev" if r.get("id") in dev else "test" if r.get("id") in test else None
            if half is None:
                continue
            stderr = "\n".join(s for s in (r.get("run_result", {}).get("stderr") or []) if s)
            for name, pat, _ in RULES:
                if re.search(pat, stderr, re.I):
                    hits[half][name] += 1
    return [{"rule": n, "dev": hits["dev"][n], "test": hits["test"][n]} for n, _, _ in RULES]


def split_analysis(data) -> dict:
    dev, test = get_split(42)
    test_ids = sorted(str(i) for i in test)
    pairs = []
    for prefix in ("doubao_mini_direct", "doubao_mini_syntax", "ds_v41f_direct", "kimik31p_direct"):
        a, b = data.get(f"{prefix}_hint_r5"), data.get(f"{prefix}_raw_r5")
        if a and b:
            ho, ro, p = mcnemar(a, b, test_ids)
            pairs.append({"config": prefix, "hint_R5": round(rate(a, test_ids), 2),
                          "raw_R5": round(rate(b, test_ids), 2), "hint_only": ho, "raw_only": ro, "p": p})
    reps = [r for r in (1, 2, 3) if f"doubao_mini_shared_hint_rep{r}" in data]
    diffs = [sum(data[f"doubao_mini_shared_hint_rep{r}"][i]["passed"] - data[f"doubao_mini_shared_raw_rep{r}"][i]["passed"]
                 for r in reps) / len(reps) for i in test_ids]
    mean, lo, hi = bootstrap_ci(diffs)
    return {"n_test": len(test_ids), "pairs": pairs,
            "shared_r0_test": {"reps": reps, "diff_pp": round(mean, 2), "ci95": [round(lo, 2), round(hi, 2)]},
            "rule_hits": rule_hits_by_split(dev, test)}


# ---------------------------------------------------------------- 2. 多重比较
def comparison_family(data) -> list[tuple[str, str, str]]:
    fam = []
    for prefix in ("doubao_mini_direct", "doubao_mini_syntax", "ds_v41f_direct", "kimik31p_direct",
                   "doubao_mini_ce_direct", "doubao_mini_ce_syntax", "ds_v41f_ce_direct"):
        for a, b in (("hint", "raw"), ("hint", "blind"), ("raw", "blind")):
            if f"{prefix}_{a}_r5" in data and f"{prefix}_{b}_r5" in data:
                fam.append((prefix, f"{prefix}_{a}_r5", f"{prefix}_{b}_r5"))
    fam.append(("compile_only", "doubao_mini_direct_hint_compileonly_r5", "doubao_mini_direct_raw_compileonly_r5"))
    for r in (1, 2, 3):
        fam.append((f"shared_rep{r}", f"doubao_mini_shared_hint_rep{r}", f"doubao_mini_shared_raw_rep{r}"))
    return [f for f in fam if f[1] in data and f[2] in data]


def multiple_comparisons(data) -> dict:
    rows = []
    for label, a, b in comparison_family(data):
        ids = sorted(set(data[a]) & set(data[b]))
        ao, bo, p = mcnemar(data[a], data[b], ids)
        rows.append({"label": label, "a": a, "b": b, "a_R5": round(rate(data[a], ids), 2),
                     "b_R5": round(rate(data[b], ids), 2), "a_only": ao, "b_only": bo, "p": p})
    primary_a = f"{PRIMARY[0]}_{PRIMARY[1]}_r5"
    primary_b = f"{PRIMARY[0]}_{PRIMARY[2]}_r5"
    primary = next(r for r in rows if r["a"] == primary_a and r["b"] == primary_b)
    secondary = [r for r in rows if r is not primary]
    for r, padj in zip(secondary, holm([r["p"] for r in secondary])):
        r["p_holm"] = padj
    return {"primary": primary, "secondary": secondary}


# ---------------------------------------------------------------- 3. 成本
def cost_table() -> list[dict]:
    out = []
    for p in sorted(glob.glob(os.path.join(EXP, "*_r5.summary.json")) + glob.glob(os.path.join(ABL, "*.summary.json"))):
        name = os.path.basename(p).replace(".summary.json", "")
        with open(p, encoding="utf-8") as f:
            s = json.load(f)
        pt, ct = s["total_prompt_tokens"], s["total_completion_tokens"]
        out.append({"name": name, "n": s["n"], "prompt_tokens": pt, "completion_tokens": ct,
                    "cost": cost_yuan(pt, ct, model_key(name))})
    return out


def attach_pass_counts(costs: list[dict], data) -> None:
    """通过数：HumanEval 与补强实验取 R5；ClassEval 取全部测试口径。"""
    for c in costs:
        name = c["name"]
        rows = data.get(name)
        if name.endswith("pass6"):
            rows6 = load(os.path.join(ABL, f"{name}.jsonl"))
            c["n_passed"] = sum(r["passed"] for r in rows6.values())
        elif rows is not None:
            c["n_passed"] = sum(round_passed(r, 5) for r in rows.values())
        else:
            c["n_passed"] = None
        tier = "peak" if "peak" in c["cost"] else "list"
        total = c["cost"][tier]
        c["cost_per_task"] = round(total / c["n"], 4)
        c["cost_per_pass"] = round(total / c["n_passed"], 4) if c.get("n_passed") else None


def budget_curves(data) -> dict:
    """token-通过率曲线：pass@k（k=1..6，期望 token = k/6 × 总量）vs 多轮修复（截止到第 k 轮）。"""
    p6 = load(os.path.join(ABL, "doubao_mini_direct_pass6.jsonl"))
    n = len(p6)
    tot6 = sum(r["usage"]["prompt_tokens"] + r["usage"]["completion_tokens"] for r in p6.values())
    passk = [{"k": k, "tokens_M": round(tot6 * k / 6 / 1e6, 3),
              "pass": round(100 * sum(pass_at_k(r["n_samples"], r["n_passed"], k) for r in p6.values()) / n, 2)}
             for k in range(1, 7)]
    curves = {"pass@k": passk}
    for name in ("doubao_mini_direct_blind_r5", "doubao_mini_direct_raw_r5", "doubao_mini_direct_hint_r5",
                 "doubao_mini_direct_hint_compileonly_r5", "doubao_mini_direct_raw_compileonly_r5"):
        rows = data[name]
        pts = []
        for k in range(6):
            tok = 0.0
            for r in rows.values():
                calls_total = calls_until(r, 99, False)
                per_call = (r["usage"]["prompt_tokens"] + r["usage"]["completion_tokens"]) / max(calls_total, 1)
                tok += per_call * calls_until(r, k, False)
            pts.append({"round": k, "tokens_M": round(tok / 1e6, 3), "pass": round(rate(rows, rows.keys(), k), 2)})
        curves[name] = pts
    return curves


# ---------------------------------------------------------------- 4. 口径
def r0_failure_kinds(data) -> dict:
    out = {}
    for name, rows in sorted(data.items()):
        hist = [r["history"][0]["failure_kind"] for r in rows.values() if r.get("history")]
        if hist:
            out[name] = dict(Counter(hist))
    return out


def fed_feedback(rows: dict[str, dict]):
    """遍历真正喂给模型的反馈（每题最后一轮的反馈不会再发给模型）。"""
    for rid, r in rows.items():
        for h in r.get("history", [])[:-1]:
            yield rid, h


def truncation(data, recompile: bool, workers: int = 4) -> dict:
    cache_path = os.path.join(OUT, "truncation_cache.json")
    cache = {}
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            cache = json.load(f)
    targets, totals = [], Counter()
    for name, rows in data.items():
        if "_blind_" in name:  # blind 不发送报错内容
            continue
        for rid, h in fed_feedback(rows):
            totals[name] += 1
            if len(h["feedback"]) >= STORED_FEEDBACK_CAP:
                targets.append((name, rid, h["round"], h["code"]))
    if recompile:
        from runner import compile_and_run, compile_only
        he = {str(k): v for k, v in load_humaneval().items()}
        ce = {str(k): v for k, v in load_classeval().items()}

        def full_len(t):
            name, rid, rnd, code = t
            key = f"{name}|{rid}|{rnd}"
            if key in cache:
                return key, cache[key]
            if "compileonly" in name:
                res = compile_only(code)
            else:
                item = (ce if "_ce_" in name else he)[rid]
                res = compile_and_run(code + "\n" + item["test"])
            return key, len(res.compile_stderr if res.failure_kind == "compile_error" else
                            (res.run_stderr + "\n" + res.run_stdout).strip())

        with ThreadPoolExecutor(workers) as ex:
            for key, n in ex.map(full_len, targets):
                cache[key] = n
        os.makedirs(OUT, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    per_exp = {}
    for name in sorted(totals):
        mine = [t for t in targets if t[0] == name]
        known = [cache.get(f"{t[0]}|{t[1]}|{t[2]}") for t in mine]
        per_exp[name] = {"fed": totals[name], "stored_capped": len(mine),
                         "over_3000": sum(1 for n in known if n is not None and n > PROMPT_FEEDBACK_CAP),
                         "unverified": sum(1 for n in known if n is None)}
    return per_exp


# ---------------------------------------------------------------- 输出
def fmt_p(p: float) -> str:
    return "<0.0001" if p < 1e-4 else f"{p:.4f}"


def write_markdown(res: dict) -> str:
    L = ["# 补充统计（零成本，自动生成）", "",
         f"价格快照：火山方舟官网在线推理（常规）单价，{PRICE_DATE}；实验实际通过 Coding Plan 订阅调用，下表为等价折算。", ""]
    s = res["split"]
    L += ["## 1. Test 半区（seed=42，N=82）hint vs raw，R5", "",
          "| 配置 | hint | raw | hint 独过 | raw 独过 | p |", "|---|---|---|---|---|---|"]
    L += [f"| {r['config']} | {r['hint_R5']:.2f}% | {r['raw_R5']:.2f}% | {r['hint_only']} | {r['raw_only']} | {fmt_p(r['p'])} |"
          for r in s["pairs"]]
    sh = s["shared_r0_test"]
    L += ["", f"共享 R0（{len(sh['reps'])} 次重复）Test 半区 hint − raw = {sh['diff_pp']:+.2f} 个百分点，"
              f"95% CI [{sh['ci95'][0]:.2f}, {sh['ci95'][1]:.2f}]", "",
          "规则在 CangjieBench 公开失败样本中的命中次数：", "", "| 规则 | Dev | Test |", "|---|---|---|"]
    L += [f"| {r['rule']} | {r['dev']} | {r['test']} |" for r in s["rule_hits"]]
    m = res["multiple"]
    p = m["primary"]
    L += ["", "## 2. 多重比较（R5，McNemar 精确检验）", "",
          f"主比较 {p['a']} vs {p['b']}：{p['a_R5']:.2f}% vs {p['b_R5']:.2f}%，"
          f"{p['a_only']}/{p['b_only']}，p = {fmt_p(p['p'])}（单独检验，α = 0.05）。", "",
          "其余比较（Holm 校正）：", "",
          "| 组别 | A | B | A% | B% | A 独过 | B 独过 | p | p (Holm) |", "|---|---|---|---|---|---|---|---|---|"]
    L += [f"| {r['label']} | {r['a']} | {r['b']} | {r['a_R5']:.2f} | {r['b_R5']:.2f} | {r['a_only']} | {r['b_only']} | "
          f"{fmt_p(r['p'])} | {fmt_p(r['p_holm'])} |" for r in m["secondary"]]
    L += ["", "## 3. 成本（元）", "", "DeepSeek 列出高峰价，括号内为空闲价；每题、每个通过题成本按高峰价。", "",
          "| 实验 | N | 输入 tokens | 输出 tokens | 总成本 | 每题 | 通过数 | 每个通过题 |", "|---|---|---|---|---|---|---|---|"]
    for c in res["cost"]:
        tot = (f"{c['cost']['peak']:.2f} ({c['cost']['offpeak']:.2f})" if "peak" in c["cost"] else f"{c['cost']['list']:.2f}")
        per_pass = f"{c['cost_per_pass']:.4f}" if c["cost_per_pass"] is not None else "-"
        npass = c["n_passed"] if c["n_passed"] is not None else "-"
        L.append(f"| {c['name']} | {c['n']} | {c['prompt_tokens']:,} | {c['completion_tokens']:,} | {tot} | "
                 f"{c['cost_per_task']:.4f} | {npass} | {per_pass} |")
    total = sum(c["cost"].get("peak", c["cost"].get("list")) for c in res["cost"])
    L += ["", f"合计（DeepSeek 按高峰价）：{total:.1f} 元", "",
          "token-通过率曲线（Doubao，HumanEval，direct；修复组按每题调用次数平均分摊 token，为近似值）：", ""]
    for name, pts in res["budget"].items():
        xs = ", ".join(f"{p['tokens_M']:.2f}M→{p['pass']:.1f}%" for p in pts)
        L.append(f"- {name}: {xs}")
    L += ["", "## 4. 口径", "", "第 0 轮失败类型分布（timeout 包含编译超时与运行超时）：", ""]
    L += [f"- {n}: {d}" for n, d in res["r0_kinds"].items()]
    L += ["", "反馈截断（只统计 raw / hint，blind 不发送报错）：", "",
          "| 实验 | 发送的反馈数 | 存储达上限 1500 | 超过 3000（被截断） | 未核实 |", "|---|---|---|---|---|"]
    L += [f"| {n} | {t['fed']} | {t['stored_capped']} | {t['over_3000']} | {t['unverified']} |"
          for n, t in res["truncation"].items()]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recompile", action="store_true", help="重新编译被截断存储的反馈以确认真实长度")
    ap.add_argument("-j", "--workers", type=int, default=4)
    args = ap.parse_args()

    data, raw = load_all(), load_raw()
    costs = cost_table()
    attach_pass_counts(costs, data)
    res = {"price_date": PRICE_DATE, "prices": PRICES,
           "split": split_analysis(data), "multiple": multiple_comparisons(data),
           "cost": costs, "budget": budget_curves(data),
           "r0_kinds": r0_failure_kinds(raw), "truncation": truncation(raw, args.recompile, args.workers)}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "extra_stats.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    md = write_markdown(res)
    with open(os.path.join(OUT, "extra_stats.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print(f"已写出 {os.path.join(OUT, 'extra_stats.md')} 与 extra_stats.json")


if __name__ == "__main__":
    main()
