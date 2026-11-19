"""第 3 阶段 / 新题集实验的统计（只读结果文件，不调用 API）。

- 只统计完整的组：summary 中 n 等于题数且 errors = 0；Kimi 例外，API 超时的题按未通过计入（TIMEOUT_AS_FAIL）。
- 每个配置（模型 × 数据集 × 起点 × 反馈）：R0、R5 的 3 次重复均值 ± 标准差，逐轮平均曲线，成本与每次通过的成本。
- 两两比较（同一模型 × 数据集 × 起点内）：先按题求 3 次重复的平均通过率，再求两组之差。
  差值的 95% CI 用按题 bootstrap（seed 0，10000 次）；p 值用按题的符号翻转置换检验（seed 0，10000 次），
  每道题只算一次，不会因合并重复而高估显著性。全部比较一起做 Holm 校正；另附逐次重复的 McNemar p 值作稳健性参考。
- 敏感性分析：去掉判定不稳定的题（FLAKY），以及每个比较中两组任一组超时的题，重算全部比较，检查结论是否不变。

用法：
  python src/stage3_stats.py                     # results/stage3/  → results/stats/stage3_stats.{md,json}
  python src/stage3_stats.py --matrix original   # results/original30/ → results/stats/original30_stats.{md,json}
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import random
import re
import statistics as st
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extra_stats import PRICE_DATE, bootstrap_ci, cost_yuan, fmt_p, holm, model_key  # noqa: E402
from run_matrix import N_TASKS, OUT_SUBDIR  # noqa: E402

from data import ROOT  # noqa: E402

OUT = os.path.join(ROOT, "results", "stats")
N_PERM = 10000
PAIRS = (("hint", "raw"), ("rag", "raw"), ("rag", "hint"), ("raw", "blind"),
         ("hint_co", "raw_co"), ("rag_co", "raw_co"))
# 判定不稳定的题（参考答案重复运行时时过时不过），只在敏感性分析中去掉：
#   HumanEval 20：测试用 != 比较 (Float64, Float64) 元组，cjc 时而接受、时而报“不支持”（约 50%）
#   ClassEval 58：扫雷参考答案随机布雷、可能重叠，方法级测试 0 检查雷数，约 1/10 不通过
FLAKY = {"he": frozenset({"20"}), "ce": frozenset({"58"})}
# Kimi-K3.1-Pro 生成慢，个别题 API 超时（HumanEval 240 秒、ClassEval 600 秒，每次调用重试 5 次）后不再补跑，
# 按未通过计入分母；其他模型仍要求 errors = 0。
TIMEOUT_AS_FAIL = frozenset({"kimik31p"})
_NAME = re.compile(r"^(.+?)_(he|ce|or)_(direct|syntax)_([a-z]+(?:_co)?)_rep(\d+)$")


def parse_name(name: str) -> tuple[str, str, str, str, int] | None:
    m = _NAME.match(name)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3), m.group(4), int(m.group(5))


def load_groups(base: str, n_tasks: dict[str, int] = N_TASKS,
                timeout_as_fail: frozenset = None) -> dict[tuple, dict[int, dict]]:
    """{(模型, 数据集, 起点, 反馈): {重复: {"curve", "passed": {id: bool}, "tokens": (输入, 输出), "timeouts"}}}

    只收 errors = 0 的组；例外是 timeout_as_fail 中的模型（默认 TIMEOUT_AS_FAIL）：出错的题若全部是 API 超时，
    就按失败计入分母。repair.py 已把这些题记为未通过且每一轮都算失败，曲线无需调整（其 token 未记录，成本略偏低）。
    """
    timeout_as_fail = TIMEOUT_AS_FAIL if timeout_as_fail is None else timeout_as_fail
    groups: dict[tuple, dict[int, dict]] = defaultdict(dict)
    for p in sorted(glob.glob(os.path.join(base, "runs", "*.summary.json"))):
        parsed = parse_name(os.path.basename(p)[: -len(".summary.json")])
        if parsed is None:
            continue
        model, ds, prompt, fb, rep = parsed
        with open(p, encoding="utf-8") as f:
            s = json.load(f)
        if s.get("n") != n_tasks.get(ds):
            continue
        if s.get("errors") != 0 and model not in timeout_as_fail:
            continue
        by_id: dict[str, dict] = {}
        with open(p[: -len(".summary.json")] + ".jsonl", encoding="utf-8") as f:
            for r in (json.loads(line) for line in f if line.strip()):
                if "error" not in r or str(r["id"]) not in by_id:   # 同 repair.py 续跑：无错误的行优先
                    by_id[str(r["id"])] = r
        errs = [str(r["error"]) for r in by_id.values() if "error" in r]
        if len(errs) != s.get("errors") or not all("Timeout" in e for e in errs):
            continue                                                  # 正在补跑，或有非超时错误
        groups[(model, ds, prompt, fb)][rep] = {
            "curve": s["pass@1_by_round"], "passed": {i: bool(r["passed"]) for i, r in by_id.items()},
            "tokens": (s.get("total_prompt_tokens", 0), s.get("total_completion_tokens", 0)),
            "timeouts": len(errs),
            "timeout_ids": frozenset(i for i, r in by_id.items() if "error" in r)}
    return dict(groups)


def per_problem_diff(a: dict[int, dict], b: dict[int, dict], exclude: frozenset = frozenset()) -> list[float]:
    """每道题：A 在各次重复中的平均通过率 − B 的平均通过率（只用两边都有的重复和题目，去掉 exclude 中的题）。"""
    reps_a, reps_b = sorted(a), sorted(b)
    ids = set.intersection(*(set(a[r]["passed"]) for r in reps_a), *(set(b[r]["passed"]) for r in reps_b)) - exclude
    return [st.mean(a[r]["passed"][i] for r in reps_a) - st.mean(b[r]["passed"][i] for r in reps_b)
            for i in sorted(ids)]


def sign_flip_p(diffs: list[float], n_perm: int = N_PERM, seed: int = 0) -> float:
    """双侧符号翻转置换检验：在“两组无差异”下每道题差值的正负号可交换。"""
    obs = abs(sum(diffs))
    if obs == 0:
        return 1.0
    rng = random.Random(seed)
    hits = sum(1 for _ in range(n_perm)
               if abs(sum(d if rng.random() < 0.5 else -d for d in diffs)) >= obs - 1e-12)
    return (hits + 1) / (n_perm + 1)


def mcnemar_exact(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def _mcnemar_per_rep(a: dict[int, dict], b: dict[int, dict]) -> list[float]:
    out = []
    for r in sorted(set(a) & set(b)):
        x, y = a[r]["passed"], b[r]["passed"]
        ids = set(x) & set(y)
        out.append(mcnemar_exact(sum(x[i] and not y[i] for i in ids), sum(y[i] and not x[i] for i in ids)))
    return out


def compare(groups: dict[tuple, dict[int, dict]], exclude: dict[str, frozenset] | None = None,
            drop_timeouts: bool = False) -> list[dict]:
    """敏感性分析用：exclude={数据集: 要去掉的题号}；drop_timeouts=True 时，两组任一次重复中超时的题从两组同时去掉。"""
    rows = []
    for model, ds, prompt in sorted({k[:3] for k in groups}):
        for fa, fb in PAIRS:
            a, b = groups.get((model, ds, prompt, fa)), groups.get((model, ds, prompt, fb))
            if not a or not b:
                continue
            ex = set((exclude or {}).get(ds, frozenset()))
            if drop_timeouts:
                ex |= {i for g in (a, b) for rep in g.values() for i in rep.get("timeout_ids", ())}
            diffs = per_problem_diff(a, b, frozenset(ex))
            mean, lo, hi = bootstrap_ci(diffs)
            rows.append({"model": model, "ds": ds, "prompt": prompt, "a": fa, "b": fb, "n": len(diffs),
                         "reps": f"{len(a)}/{len(b)}", "diff": round(mean, 2), "ci_lo": round(lo, 2),
                         "ci_hi": round(hi, 2), "p": sign_flip_p(diffs),
                         "mcnemar_per_rep": [round(p, 4) for p in _mcnemar_per_rep(a, b)]})
    for r, ph in zip(rows, holm([r["p"] for r in rows])):
        r["p_holm"] = ph
    return rows


def summarize(groups: dict[tuple, dict[int, dict]]) -> list[dict]:
    rows = []
    for key in sorted(groups):
        reps = groups[key]
        curves = [reps[r]["curve"] for r in sorted(reps)]
        r5 = [c[-1] for c in curves]
        pin = sum(reps[r]["tokens"][0] for r in reps)
        pout = sum(reps[r]["tokens"][1] for r in reps)
        n_pass = sum(sum(reps[r]["passed"].values()) for r in reps)
        yuan = cost_yuan(pin, pout, model_key(key[0]))
        rows.append({"model": key[0], "ds": key[1], "prompt": key[2], "feedback": key[3], "reps": len(reps),
                     "timeouts": sum(reps[r].get("timeouts", 0) for r in reps),
                     "r0": curves[0][0], "r5_mean": round(st.mean(r5), 2),
                     "r5_sd": round(st.stdev(r5), 2) if len(r5) > 1 else 0.0,
                     "curve_mean": [round(st.mean(c[k] for c in curves), 2) for k in range(len(curves[0]))],
                     "tokens": (pin, pout), "yuan": yuan,
                     "yuan_per_pass": max(yuan.values()) / n_pass if n_pass else None})
    return rows


def write_markdown(summary: list[dict], comps: list[dict], title: str, sens: list[dict] | None = None) -> str:
    L = [f"# {title}（自动生成）", "",
         "只统计完整的组（n 等于题数且 errors = 0）。R5 为最多修复 5 轮后的通过率，3 次重复取均值 ± 标准差。",
         f"成本按火山方舟官网在线推理单价折算（{PRICE_DATE}），DeepSeek 取高峰价（偏保守）；实验实际通过 Coding Plan 订阅调用。", ""]
    timed_out = [r for r in summary if r.get("timeouts")]
    if timed_out:
        L += ["API 超时按未通过计入分母（只对 " + "、".join(sorted(TIMEOUT_AS_FAIL)) + "，不补跑）：" + "；".join(
            f"{r['model']} {r['ds']} {r['prompt']} {r['feedback']} {r['timeouts']} 题次" for r in timed_out) + "。", ""]
    L += [
         "## 各配置通过率", "",
         "| 模型 | 数据集 | 起点 | 反馈 | 重复 | R0 | R5 均值 ± sd | 逐轮平均 | 元/次通过 |", "|---|---|---|---|---|---|---|---|---|"]
    for r in summary:
        ypp = f"{r['yuan_per_pass']:.4f}" if r["yuan_per_pass"] is not None else "—"
        L.append(f"| {r['model']} | {r['ds']} | {r['prompt']} | {r['feedback']} | {r['reps']} | {r['r0']:.2f} | "
                 f"{r['r5_mean']:.2f} ± {r['r5_sd']:.2f} | {' → '.join(f'{x:.1f}' for x in r['curve_mean'])} | {ypp} |")
    L += ["", "## 两两比较", "",
          "差值 = A − B（百分点），按题平均 3 次重复后计算；95% CI 为按题 bootstrap；p 为按题符号翻转置换检验；"
          f"p(Holm) 在下表全部 {len(comps)} 个比较上校正；最后一列为逐次重复 McNemar p 值（稳健性参考，未校正）。", "",
          "| 模型 | 数据集 | 起点 | A vs B | 题数 | 差值 [95% CI] | p | p(Holm) | 逐次重复 McNemar |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in comps:
        L.append(f"| {r['model']} | {r['ds']} | {r['prompt']} | {r['a']} vs {r['b']} | {r['n']} | "
                 f"{r['diff']:+.2f} [{r['ci_lo']:+.2f}, {r['ci_hi']:+.2f}] | {fmt_p(r['p'])} | {fmt_p(r['p_holm'])} | "
                 f"{', '.join(fmt_p(p) for p in r['mcnemar_per_rep'])} |")
    if sens:
        flaky = sorted((ds, ids) for ds, ids in FLAKY.items() if ds in {r["ds"] for r in comps})
        flaky_note = ("去掉 " + "、".join(f"{ds} 第 {', '.join(sorted(ids))} 题" for ds, ids in flaky)
                      + "（参考答案重复运行时判定不稳定，原因见 stage3_stats.py 中 FLAKY 的注释）；并且") if flaky else ""
        L += ["", "## 敏感性分析：去掉判定不稳定的题和超时的题", "",
              flaky_note + "每个比较中，两组任一次重复里 API 超时的题从两组同时去掉（只有 "
              + "、".join(sorted(TIMEOUT_AS_FAIL)) + " 有超时）。然后重新计算两两比较与 Holm 校正。", "",
              "| 模型 | 数据集 | 起点 | A vs B | 差值（全部题） | p(Holm)（全部题） | 题数 | 差值（去掉后） | p(Holm)（去掉后） |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r, s in zip(comps, sens):
            L.append(f"| {r['model']} | {r['ds']} | {r['prompt']} | {r['a']} vs {r['b']} | {r['diff']:+.2f} | "
                     f"{fmt_p(r['p_holm'])} | {s['n']} | {s['diff']:+.2f} | {fmt_p(s['p_holm'])} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", choices=sorted(OUT_SUBDIR), default="stage3")
    ap.add_argument("--base", help="结果目录（默认 results/<stage3|original30>）")
    ap.add_argument("--out", default=OUT, help="输出目录（默认 results/stats）")
    args = ap.parse_args()
    base = args.base or os.path.join(ROOT, "results", OUT_SUBDIR[args.matrix])
    groups = load_groups(base)
    summary, comps, sens = summarize(groups), compare(groups), compare(groups, FLAKY, drop_timeouts=True)
    os.makedirs(args.out, exist_ok=True)
    stem = os.path.join(args.out, f"{OUT_SUBDIR[args.matrix]}_stats")
    with open(stem + ".json", "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "comparisons": comps, "sensitivity_excl_flaky": sens},
                  f, ensure_ascii=False, indent=1)
    title = "第 3 阶段实验统计" if args.matrix == "stage3" else "新题集 Original-30 实验统计"
    with open(stem + ".md", "w", encoding="utf-8") as f:
        f.write(write_markdown(summary, comps, title, sens))
    print(f"{len(groups)} 个配置，{len(comps)} 个比较 → {stem}.md")


if __name__ == "__main__":
    main()
