"""审稿后补充实验（results/review/）的统计，按 docs/补充实验统计方案.md 预先设定的三个比较族实现。

- 族 G（推广到其他模型）：新模型与重跑的 Kimi 各格内 hint/rag/raw/blind 比较（同第 3 阶段），另加 DeepSeek ClassEval syntax；
- 族 A（Agent 基线）：agent vs rag、agent15 vs agent；
- 族 R（改进检索）：rag2 vs rag。
各族分别做 Holm；敏感性分析：三族合并做 Holm，去掉不稳定题与超时题后重算。

配对：DeepSeek / Doubao-mini 的 agent / agent15 / rag2 复用第 3 阶段、Original-30 的共享第 0 轮，
与那里的原有组逐题配对；其余模型只用 review 自己的组（第 3 阶段旧的 Kimi 数据不合并）。

用法：
  python src/review_stats.py            # → results/stats/review_stats.{md,json}
  python src/review_stats.py --pilot    # 试跑数据（每组 10 题）→ results/review/pilot/stats/（不进 git）
"""
from __future__ import annotations

import argparse
import json
import os
import statistics as st
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extra_stats import bootstrap_ci, fmt_p, holm  # noqa: E402
from run_matrix import AGENT_ARMS, N_TASKS, NEW_MODELS, PILOT_LIMIT, expand_matrix  # noqa: E402
from stage3_stats import (FLAKY, PAIRS, compare, load_groups, load_r0_tokens, parse_name,  # noqa: E402
                          sign_flip_p, summarize)

from data import ROOT  # noqa: E402

RESULTS = os.path.join(ROOT, "results")
REUSE_R0 = ("ds_v41f", "doubao_mini")           # 复用第 3 阶段 / Original-30 第 0 轮的模型
FAMILIES = {
    "G": ("推广到其他模型", PAIRS),
    "A": ("Agent 基线", (("agent", "rag"), ("agent15", "agent"))),
    "R": ("改进检索 rag2", (("rag2", "rag"),)),
}


def bases(pilot: bool) -> tuple[str, list[str]]:
    sub = "pilot" if pilot else ""
    return (os.path.join(RESULTS, "review", sub),
            [os.path.join(RESULTS, m, sub) for m in ("stage3", "original30")])


def load_all(review: str, olds: list[str], n_tasks: dict[str, int]) -> dict[tuple, dict[int, dict]]:
    """review 的组 + 原有矩阵中 REUSE_R0 模型的组（review 中已有的键以 review 为准）。"""
    groups = load_groups(review, n_tasks)
    for base in olds:
        for key, reps in load_groups(base, n_tasks).items():
            if key[0] in REUSE_R0 and key not in groups:
                groups[key] = reps
    return groups


def load_all_r0(review: str, olds: list[str]) -> dict[tuple, tuple[int, int]]:
    r0 = {k: v for base in olds for k, v in load_r0_tokens(base).items() if k[0] in REUSE_R0}
    r0.update(load_r0_tokens(review))
    return r0


def family_groups(groups: dict[tuple, dict], fam: str) -> dict[tuple, dict]:
    """族 G 只含新模型、重跑的 Kimi 与 DeepSeek ClassEval syntax，以免重复第 3 阶段已有的比较；族 A、R 含全部模型。"""
    if fam != "G":
        return groups
    return {k: v for k, v in groups.items()
            if k[0] in NEW_MODELS + ("kimik31p",) or k[:3] == ("ds_v41f", "ce", "syntax")}


def run_families(groups: dict[tuple, dict], **kw) -> list[dict]:
    """各族内分别做 Holm（p_holm），再在三族合并后做一次 Holm（p_holm_all，敏感性分析）。"""
    rows = []
    for fam, (_, pairs) in FAMILIES.items():
        rows += [{**r, "family": fam} for r in compare(family_groups(groups, fam), pairs=pairs, **kw)]
    for r, ph in zip(rows, holm([r["p"] for r in rows])):
        r["p_holm_all"] = ph
    return rows


def _means(reps: dict[int, dict]) -> dict[str, float]:
    ids = set.intersection(*(set(reps[r]["passed"]) for r in reps))
    return {i: st.mean(reps[r]["passed"][i] for r in reps) for i in ids}


def interaction(groups: dict[tuple, dict]) -> list[dict]:
    """syntax × hint 交互（方案第六节）：每题 I = (hint − raw)_direct − (hint − raw)_syntax（单位：百分点）。
    REUSE_R0 模型的数据已看过，记为探索性（family "I-explore"）；其余为验证性族 "I"。两族各自 Holm。"""
    rows = []
    for model, ds in sorted({k[:2] for k in groups}):
        arms = [groups.get((model, ds, p, fb)) for p in ("direct", "syntax") for fb in ("hint", "raw")]
        if not all(arms):
            continue
        m = [_means(a) for a in arms]
        ids = sorted(set.intersection(*(set(x) for x in m)))
        diffs = [(m[0][i] - m[1][i]) - (m[2][i] - m[3][i]) for i in ids]
        mean, lo, hi = bootstrap_ci(diffs)
        rows.append({"family": "I-explore" if model in REUSE_R0 else "I", "model": model, "ds": ds, "n": len(ids),
                     "hint_gain_direct": round(100 * st.mean(m[0][i] - m[1][i] for i in ids), 2),
                     "hint_gain_syntax": round(100 * st.mean(m[2][i] - m[3][i] for i in ids), 2),
                     "interaction": round(mean, 2), "ci_lo": round(lo, 2), "ci_hi": round(hi, 2),
                     "p": sign_flip_p(diffs)})
    for fam in ("I", "I-explore"):
        sub = [r for r in rows if r["family"] == fam]
        for r, ph in zip(sub, holm([r["p"] for r in sub])):
            r["p_holm"] = ph
    return rows


def _rows(path: str) -> dict[str, dict]:
    by_id: dict[str, dict] = {}
    with open(path, encoding="utf-8") as f:
        for r in (json.loads(line) for line in f if line.strip()):
            if "error" not in r or str(r["id"]) not in by_id:
                by_id[str(r["id"])] = r
    return by_id


def agent_behavior(groups: dict[tuple, dict], review: str) -> list[dict]:
    """Agent 组的行为：每题平均检索次数、至少检索一次的题占比、无效动作、实际用掉的步数（第 0 轮之后的历史条数）。"""
    out = []
    for key in sorted(k for k in groups if k[3] in AGENT_ARMS):
        acts, steps, searched = Counter(), [], 0
        for rep in sorted(groups[key]):
            for r in _rows(os.path.join(review, "runs", f"{'_'.join(key)}_rep{rep}.jsonl")).values():
                hist = [h for h in r.get("history") or [] if str(h.get("round")) != "0"]
                c = Counter(h.get("action") for h in hist)
                acts += c
                searched += c["search"] > 0
                steps.append(len(hist))
        n = len(steps)
        out.append({"model": key[0], "ds": key[1], "prompt": key[2], "feedback": key[3], "problems": n,
                    "search_per_problem": round(acts["search"] / n, 3) if n else None,
                    "pct_any_search": round(100 * searched / n, 1) if n else None,
                    "invalid": acts["invalid"], "mean_steps": round(st.mean(steps), 2) if n else None})
    return out


def missing_groups(groups: dict[tuple, dict]) -> list[str]:
    """review 矩阵中应有、但尚未完整（不足 3 次重复）的组。"""
    _, jobs = expand_matrix("review")
    want = Counter(parse_name(j.name)[:4] for j in jobs)
    return sorted("_".join(k) + f"（{len(groups.get(k, {}))}/{c}）" for k, c in want.items()
                  if len(groups.get(k, {})) < c)


def _cmp_table(rows: list[dict], sens: list[dict]) -> list[str]:
    L = ["| 模型 | 数据集 | 起点 | A vs B | 题数 | 差值 [95% CI] | p | p(Holm，族内) | p(Holm，三族合并) | "
         "差值 / p(Holm)（去掉不稳定与超时题） |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r, s in zip(rows, sens):
        L.append(f"| {r['model']} | {r['ds']} | {r['prompt']} | {r['a']} vs {r['b']} | {r['n']} | "
                 f"{r['diff']:+.2f} [{r['ci_lo']:+.2f}, {r['ci_hi']:+.2f}] | {fmt_p(r['p'])} | {fmt_p(r['p_holm'])} | "
                 f"{fmt_p(r['p_holm_all'])} | {s['diff']:+.2f} / {fmt_p(s['p_holm'])} |")
    return L


def write_markdown(res: dict, pilot: bool) -> str:
    L = ["# 补充实验统计（自动生成）" + ("——试跑数据，每组 10 题，仅用于检查流程" if pilot else ""), "",
         "按 docs/补充实验统计方案.md 预先设定的比较族计算；方法同 stage3_stats（按题平均 3 次重复后求差，"
         "bootstrap CI，符号翻转置换检验）。成本含共享第 0 轮，rag2 另计查询改写调用。"
         "DeepSeek / Doubao-mini 的原有组取自第 3 阶段与 Original-30。", ""]
    if res["missing"]:
        L += [f"尚未完整的组（{len(res['missing'])} 个，括号内为已完成重复数 / 应有重复数）：" + "、".join(res["missing"]), ""]
    L += ["## 各配置通过率与成本", "",
          "| 模型 | 数据集 | 起点 | 反馈 | 重复 | 超时题次 | R0 | R5 均值 ± sd | 美元/解（含 R0） |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in res["summary"]:
        yps = f"{r['usd_per_solve_with_r0']:.4f}" if r.get("usd_per_solve_with_r0") is not None else "—"
        L.append(f"| {r['model']} | {r['ds']} | {r['prompt']} | {r['feedback']} | {r['reps']} | {r['timeouts']} | "
                 f"{r['r0']:.2f} | {r['r5_mean']:.2f} ± {r['r5_sd']:.2f} | {yps} |")
    for fam, (title, _) in FAMILIES.items():
        rows = [(r, s) for r, s in zip(res["comparisons"], res["sensitivity_excl_flaky"]) if r["family"] == fam]
        L += ["", f"## 族 {fam}：{title}（{len(rows)} 个比较，Holm 在族内校正）", ""]
        L += _cmp_table([r for r, _ in rows], [s for _, s in rows]) if rows else ["（暂无可比较的组）"]
    L += ["", "## syntax × hint 交互效应", "",
          "I = (hint − raw)<sub>direct</sub> − (hint − raw)<sub>syntax</sub>（百分点，按题计算）；I > 0 表示有语法手册时 hint 的增益更小。"
          "族 I 为验证性（族内 Holm）；I-explore 的数据已在第 3 阶段看过，只作探索性参考（单独 Holm）。", "",
          "| 族 | 模型 | 数据集 | 题数 | hint 增益（direct） | hint 增益（syntax） | 交互 I [95% CI] | p | p(Holm) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in res.get("interaction", []):
        L.append(f"| {r['family']} | {r['model']} | {r['ds']} | {r['n']} | {r['hint_gain_direct']:+.2f} | "
                 f"{r['hint_gain_syntax']:+.2f} | {r['interaction']:+.2f} [{r['ci_lo']:+.2f}, {r['ci_hi']:+.2f}] | "
                 f"{fmt_p(r['p'])} | {fmt_p(r['p_holm'])} |")
    L += ["", "## Agent 行为（描述性）", "",
          "| 模型 | 数据集 | 起点 | 组 | 题次 | 每题检索次数 | 至少检索一次 | 无效动作 | 平均步数 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in res["agent_behavior"]:
        L.append(f"| {r['model']} | {r['ds']} | {r['prompt']} | {r['feedback']} | {r['problems']} | "
                 f"{r['search_per_problem']} | {r['pct_any_search']}% | {r['invalid']} | {r['mean_steps']} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true", help="统计试跑数据（每组 10 题）")
    args = ap.parse_args()
    review, olds = bases(args.pilot)
    n_tasks = {ds: PILOT_LIMIT for ds in N_TASKS} if args.pilot else N_TASKS
    groups = load_all(review, olds, n_tasks)
    res = {"summary": summarize(groups, load_all_r0(review, olds)),
           "comparisons": run_families(groups),
           "sensitivity_excl_flaky": run_families(groups, exclude=FLAKY, drop_timeouts=True),
           "interaction": interaction(groups),
           "agent_behavior": agent_behavior(groups, review),
           "missing": [] if args.pilot else missing_groups(groups)}
    out = os.path.join(review, "stats") if args.pilot else os.path.join(RESULTS, "stats")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "review_stats.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, "review_stats.md"), "w", encoding="utf-8") as f:
        f.write(write_markdown(res, args.pilot))
    print(f"{len(groups)} 个配置，{len(res['comparisons'])} 个比较，未完整 {len(res['missing'])} 组 → {out}")


if __name__ == "__main__":
    main()
