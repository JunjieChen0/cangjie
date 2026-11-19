"""延长修复轮数补充实验（Doubao HumanEval direct 起点，raw / hint / rag 各 3 次，最多 10 轮）的统计与曲线图。

- 从与第 3 阶段相同的共享第 0 轮出发（--init results/stage3/r0/doubao_mini_he_direct_r0.jsonl），温度 0.3；
  因为是重新采样，前 5 轮与第 3 阶段主实验数字不同，只单独报告，不并入主表。
- 每种反馈：R5、R10 均值 ± SD，0–10 轮平均曲线与逐轮增量，修复阶段 token，含共享第 0 轮的美元/解。
- 第 10 轮两两比较（hint vs raw、rag vs raw、rag vs hint）沿用 stage3_stats.compare 的方法，在这 3 个比较内单独做 Holm。
- 图：results/figures/fig5_rounds10_curve.png（均值，阴影为 ± SD，虚线为主实验的 5 轮上限）。

用法：python src/rounds10_stats.py
"""
from __future__ import annotations

import json
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import ROOT  # noqa: E402
from extra_stats import fmt_p  # noqa: E402
from stage3_stats import compare, load_groups, load_r0_tokens, run_cost  # noqa: E402

BASE = os.path.join(ROOT, "results", "rounds10")
R0_BASE = os.path.join(ROOT, "results", "stage3")
OUT = os.path.join(ROOT, "results", "stats")
FIG = os.path.join(ROOT, "results", "figures", "fig5_rounds10_curve.png")
MAIN_ROUNDS = 5


def round_gains(curve: list[float]) -> list[float]:
    """逐轮增量（第 k 轮 − 第 k−1 轮）。"""
    return [round(b - a, 2) for a, b in zip(curve, curve[1:])]


def _sd(xs: list[float]) -> float:
    return round(st.stdev(xs), 2) if len(xs) > 1 else 0.0


def feedback_rows(groups: dict[tuple, dict[int, dict]], r0_tokens: dict[tuple, tuple[int, int]]) -> list[dict]:
    rows = []
    for key in sorted(groups):
        reps = groups[key]
        curves = [reps[r]["curve"] for r in sorted(reps)]
        r5, r10 = [c[MAIN_ROUNDS] for c in curves], [c[-1] for c in curves]
        mean = [round(st.mean(c[k] for c in curves), 2) for k in range(len(curves[0]))]
        run = run_cost(reps, r0_tokens[key[:3]], key[0])
        solved = st.mean(sum(reps[r]["passed"].values()) for r in reps)
        rows.append({"model": key[0], "ds": key[1], "prompt": key[2], "feedback": key[3], "reps": len(reps),
                     "r0": curves[0][0], "r5_mean": round(st.mean(r5), 2), "r5_sd": _sd(r5),
                     "r10_mean": round(st.mean(r10), 2), "r10_sd": _sd(r10), "curve_mean": mean,
                     "gains": round_gains(mean),
                     "repair_tokens_mean": round(st.mean(sum(reps[r]["tokens"]) for r in reps)),
                     "run_usd_with_r0": run, "usd_per_solve_with_r0": run / solved if solved else None})
    return rows


def write_markdown(rows: list[dict], comps: list[dict]) -> str:
    L = ["# 延长修复轮数补充实验统计（自动生成）", "",
         "Doubao-Seed-2.0-Mini，HumanEval `direct` 起点，从第 3 阶段共享第 0 轮出发，最多修复 10 轮，温度 0.3，每种反馈 3 次重复。"
         "重新采样，前 5 轮与第 3 阶段主实验数字不同，单独报告。", "",
         "| 反馈 | 重复 | R0 | R5 均值 ± SD | R10 均值 ± SD | 修复 token（每次平均） | 美元/解（含 R0） |",
         "|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['feedback']} | {r['reps']} | {r['r0']:.2f} | {r['r5_mean']:.2f} ± {r['r5_sd']:.2f} | "
                 f"{r['r10_mean']:.2f} ± {r['r10_sd']:.2f} | {r['repair_tokens_mean']:,} | {r['usd_per_solve_with_r0']:.4f} |")
    L += ["", "## 逐轮平均通过率与增量", "", "| 反馈 | R0 → R10 平均通过率 | 第 6–10 轮每轮增量 |", "|---|---|---|"]
    for r in rows:
        L.append(f"| {r['feedback']} | {' → '.join(f'{x:.1f}' for x in r['curve_mean'])} | "
                 f"{', '.join(f'{g:+.2f}' for g in r['gains'][MAIN_ROUNDS:])} |")
    if comps:
        L += ["", "## 第 10 轮两两比较", "",
              f"方法同 stage3_stats（按题平均重复后求差，bootstrap CI，符号翻转置换检验）；p(Holm) 只在下表 {len(comps)} 个比较内校正。", "",
              "| A vs B | 题数 | 差值 [95% CI] | p | p(Holm) |", "|---|---|---|---|---|"]
        for c in comps:
            L.append(f"| {c['a']} vs {c['b']} | {c['n']} | {c['diff']:+.2f} [{c['ci_lo']:+.2f}, {c['ci_hi']:+.2f}] | "
                     f"{fmt_p(c['p'])} | {fmt_p(c['p_holm'])} |")
    return "\n".join(L) + "\n"


def plot(groups: dict[tuple, dict[int, dict]], path: str = FIG) -> None:
    from plot_figures import FB_NAME, FB_STYLE, curve_band, plt
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    for fb in ("raw", "hint", "rag"):
        reps = groups.get(("doubao_mini", "he", "direct", fb))
        if not reps:
            continue
        mean, sd = curve_band(reps)
        ls, mk, col = FB_STYLE[fb]
        xs = range(len(mean))
        ax.plot(xs, mean, linestyle=ls, marker=mk, color=col, linewidth=1.8, markersize=5,
                label=f"{FB_NAME[fb]} (R10 {mean[-1]:.1f}%)")
        ax.fill_between(xs, [m - s for m, s in zip(mean, sd)], [m + s for m, s in zip(mean, sd)],
                        color=col, alpha=0.15, linewidth=0)
    ax.axvline(MAIN_ROUNDS, color="#7f7f7f", linestyle=":", linewidth=1)
    ax.text(MAIN_ROUNDS + 0.1, 3, "main protocol\n(5 rounds)", fontsize=8, color="#7f7f7f")
    ax.set_xticks(range(11))
    ax.set_xlabel("Repair round")
    ax.set_ylabel("Pass@1 (%)")
    ax.set_ylim(0, 100)
    ax.set_title("Doubao-Seed-2.0-Mini, HumanEval, direct start\n(10 repair rounds, 3 runs)", fontsize=10.5)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main():
    groups = load_groups(BASE)
    rows, comps = feedback_rows(groups, load_r0_tokens(R0_BASE)), compare(groups)
    os.makedirs(OUT, exist_ok=True)
    stem = os.path.join(OUT, "rounds10_stats")
    with open(stem + ".json", "w", encoding="utf-8") as f:
        json.dump({"feedback": rows, "comparisons_r10": comps}, f, ensure_ascii=False, indent=1)
    with open(stem + ".md", "w", encoding="utf-8") as f:
        f.write(write_markdown(rows, comps))
    plot(groups)
    print(f"{len(groups)} 种反馈，{len(comps)} 个比较 → {stem}.md，{FIG}")


if __name__ == "__main__":
    main()
