"""生成论文插图（第 3 阶段数据，英文标注，输出到 results/figures/）：
1. fig1_rounds_curve.png           — HumanEval：各模型 × 起点下四种反馈的 0–5 轮 Pass@1（3 次重复均值 ± SD）
2. fig2_cost_pareto.png            — 每次完整运行的成本（美元）vs R5 通过率（HumanEval / ClassEval）
3. fig3_error_repair.png           — Doubao HumanEval direct：按第 0 轮错误类别的修复成功率
4. fig4_rounds_curve_classeval.png — ClassEval（全部测试口径）：0–5 轮 Pass@1

数据来自 results/stage3/（与 stage3_stats.py 同一筛选口径：完整且 errors = 0，Kimi 超时按失败计）。
用法：python src/plot_figures.py
"""
from __future__ import annotations

import json
import os
import statistics as st
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import classify_error  # noqa: E402
from data import ROOT  # noqa: E402
from stage3_stats import load_groups, run_cost  # noqa: E402

BASE = os.path.join(ROOT, "results", "stage3")
OUT_DIR = os.path.join(ROOT, "results", "figures")
MODELS = {"ds_v41f": "DeepSeek-V4.1-Flash", "doubao_mini": "Doubao-Seed-2.0-Mini", "kimik31p": "Kimi-K3.1-Pro"}
MODEL_COLOR = {"ds_v41f": "#1f77b4", "doubao_mini": "#d62728", "kimik31p": "#2ca02c"}
FEEDBACKS = ("blind", "raw", "hint", "rag")
FB_NAME = {"blind": "Blind", "raw": "Raw", "hint": "Hint", "rag": "RAG"}
FB_STYLE = {"blind": (":", "x", "#7f7f7f"), "raw": ("--", "^", "#ff7f0e"),
            "hint": ("-", "s", "#1f77b4"), "rag": ("-", "o", "#2ca02c")}
ERROR_CATS = (("foreign_syntax", "Foreign syntax"), ("api_or_undeclared", "API / undeclared"),
              ("other", "Other"))
MIN_CAT_SIZE = 10   # 题数少于此的类别并入 Other，避免小样本类别的比例误导
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.unicode_minus": False})


def curve_band(reps: dict[int, dict]) -> tuple[list[float], list[float]]:
    """各轮通过率在重复间的均值与标准差（只有 1 次重复时标准差为 0）。"""
    curves = [reps[r]["curve"] for r in sorted(reps)]
    mean = [st.mean(c[k] for c in curves) for k in range(len(curves[0]))]
    sd = [st.stdev(c[k] for c in curves) if len(curves) > 1 else 0.0 for k in range(len(curves[0]))]
    return mean, sd


def error_repair_rates(cats: dict[str, str], reps: dict[int, dict]) -> dict[str, tuple[int, float, float]]:
    """cats：{题号: 第 0 轮错误类别}（来自共享第 0 轮）。返回 {类别: (题数, 修复成功率均值 %, 标准差)}。"""
    out = {}
    for cat in sorted(set(cats.values())):
        ids = [i for i, c in cats.items() if c == cat]
        rates = [100 * sum(reps[r]["passed"].get(i, False) for i in ids) / len(ids) for r in sorted(reps)]
        out[cat] = (len(ids), st.mean(rates), st.stdev(rates) if len(rates) > 1 else 0.0)
    return out


def merge_small_categories(cats: dict[str, str], min_size: int = MIN_CAT_SIZE) -> dict[str, str]:
    """题数少于 min_size 的错误类别统一改为 "other"。"""
    sizes = {c: sum(1 for v in cats.values() if v == c) for c in set(cats.values())}
    return {i: (c if sizes[c] >= min_size else "other") for i, c in cats.items()}


def load_r0(name: str) -> tuple[dict, list[dict]]:
    stem = os.path.join(BASE, "r0", name + "_r0")
    with open(stem + ".summary.json", encoding="utf-8") as f:
        s = json.load(f)
    with open(stem + ".jsonl", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    return s, rows


def _plot_panel(ax, groups, model, ds, prompt, title):
    for fb in FEEDBACKS:
        reps = groups.get((model, ds, prompt, fb))
        if not reps:
            continue
        mean, sd = curve_band(reps)
        ls, mk, col = FB_STYLE[fb]
        xs = range(len(mean))
        ax.plot(xs, mean, linestyle=ls, marker=mk, color=col, linewidth=1.8, markersize=5,
                label=f"{FB_NAME[fb]} ({mean[-1]:.1f}%)")
        if any(sd):
            ax.fill_between(xs, [m - s for m, s in zip(mean, sd)], [m + s for m, s in zip(mean, sd)],
                            color=col, alpha=0.15, linewidth=0)
    ax.set_title(title, fontsize=10.5)
    ax.set_xticks(range(6))
    ax.set_ylim(0, 102)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="best", fontsize=8)


def plot_he_curves(groups):
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.4), sharex=True, sharey=True)
    for row, prompt in enumerate(("direct", "syntax")):
        for col, model in enumerate(MODELS):
            ax = axes[row][col]
            if (model, "he", prompt, "raw") not in groups:
                ax.axis("off")
                ax.text(0.5, 0.5, f"{MODELS[model]}\n'{prompt}' start not run", ha="center", va="center",
                        transform=ax.transAxes, color="#7f7f7f")
                continue
            reps = "1 run" if len(groups[(model, "he", prompt, "raw")]) == 1 else "3 runs"
            _plot_panel(ax, groups, model, "he", prompt, f"{MODELS[model]}\n{prompt} start ({reps})")
        axes[row][0].set_ylabel("Pass@1 (%)")
    for ax in axes[1]:
        ax.set_xlabel("Repair round")
    axes[0][2].set_xlabel("Repair round")
    axes[0][2].xaxis.set_tick_params(labelbottom=True)
    fig.suptitle("Pass@1 over repair rounds on HumanEval-Cangjie (N = 164, shared round 0, mean ± SD)",
                 fontsize=12.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig1_rounds_curve.png"), dpi=200)
    plt.close(fig)


def plot_ce_curves(groups):
    panels = [(m, p) for m in MODELS for p in ("direct", "syntax") if (m, "ce", p, "raw") in groups]
    fig, axes = plt.subplots(1, len(panels), figsize=(4.4 * len(panels), 4.3), sharey=True)
    for ax, (model, prompt) in zip(axes, panels):
        reps = "1 run" if len(groups[(model, "ce", prompt, "raw")]) == 1 else "3 runs"
        _plot_panel(ax, groups, model, "ce", prompt, f"{MODELS[model]}\n{prompt} start ({reps})")
        ax.set_xlabel("Repair round")
    axes[0].set_ylabel("Pass@1, all tests (%)")
    fig.suptitle("Pass@1 over repair rounds on ClassEval-Cangjie (N = 84, all-tests protocol)", fontsize=12.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig4_rounds_curve_classeval.png"), dpi=200)
    plt.close(fig)


def plot_cost(groups):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    r0_cache = {}
    for ax, (ds, title) in zip(axes, (("he", "HumanEval-Cangjie (N = 164)"), ("ce", "ClassEval-Cangjie (N = 84)"))):
        for (model, d, prompt, fb), reps in sorted(groups.items()):
            if d != ds or fb not in FEEDBACKS:
                continue
            key = f"{model}_{ds}_{prompt}"
            if key not in r0_cache:
                s, _ = load_r0(key)
                r0_cache[key] = (s["total_prompt_tokens"], s["total_completion_tokens"])
            x = run_cost(reps, r0_cache[key], model)
            r5 = [reps[r]["curve"][-1] for r in sorted(reps)]
            y, err = st.mean(r5), (st.stdev(r5) if len(r5) > 1 else 0.0)
            col = MODEL_COLOR[model]
            ax.errorbar(x, y, yerr=err, fmt=FB_STYLE[fb][1], markersize=8, color=col, capsize=2,
                        markerfacecolor=col if prompt == "direct" else "white", markeredgewidth=1.5)
        ax.set_xscale("log")
        ax.xaxis.set_major_locator(LogLocator(subs=(1, 2, 5)))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("Cost of one full run (USD, log scale)")
        ax.set_ylim(0, 102)
        ax.grid(True, which="both", linestyle="--", alpha=0.35)
    axes[0].set_ylabel("Pass@1 after 5 rounds (%)")
    handles = [Line2D([], [], color=c, marker="o", linestyle="", label=MODELS[m]) for m, c in MODEL_COLOR.items()]
    handles += [Line2D([], [], color="black", marker=FB_STYLE[f][1], linestyle="", label=FB_NAME[f]) for f in FEEDBACKS]
    handles += [Line2D([], [], color="black", marker="o", linestyle="", label="direct start"),
                Line2D([], [], color="black", marker="o", markerfacecolor="white", linestyle="", label="syntax start")]
    fig.legend(handles=handles, loc="lower center", ncol=9, fontsize=8.5, frameon=False)
    fig.suptitle("Cost vs. effectiveness (shared round 0 + repair, list price, mean ± SD)", fontsize=12.5)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(os.path.join(OUT_DIR, "fig2_cost_pareto.png"), dpi=200)
    plt.close(fig)


def plot_error_repair(groups):
    _, rows = load_r0("doubao_mini_he_direct")
    cats = {str(r["id"]): classify_error(r["history"][0]) for r in rows if r.get("history")}
    cats = merge_small_categories({i: c for i, c in cats.items() if c != "passed"})
    fig, ax = plt.subplots(figsize=(8, 4.6))
    w = 0.2
    for k, fb in enumerate(FEEDBACKS):
        rates = error_repair_rates(cats, groups[("doubao_mini", "he", "direct", fb)])
        xs = [j + (k - 1.5) * w for j in range(len(ERROR_CATS))]
        ys = [rates.get(c, (0, 0.0, 0.0))[1] for c, _ in ERROR_CATS]
        es = [rates.get(c, (0, 0.0, 0.0))[2] for c, _ in ERROR_CATS]
        bars = ax.bar(xs, ys, width=w, yerr=es, capsize=2, color=FB_STYLE[fb][2], label=FB_NAME[fb])
        for b, y, e in zip(bars, ys, es):
            ax.text(b.get_x() + b.get_width() / 2, y + e + 1.5, f"{y:.0f}", ha="center", va="bottom", fontsize=7.5)
    counts = {c: sum(1 for v in cats.values() if v == c) for c, _ in ERROR_CATS}
    ax.set_xticks(range(len(ERROR_CATS)))
    ax.set_xticklabels([f"{name}\n(n = {counts[c]})" for c, name in ERROR_CATS])
    ax.set_ylim(0, 110)
    ax.set_ylabel("Repaired within 5 rounds (%)")
    ax.set_title("Doubao-Seed-2.0-Mini, HumanEval direct start: repair rate by round-0 error category\n"
                 "(mean ± SD of 3 runs; categories from the shared round 0)", fontsize=10.5)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.legend(ncol=4, fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig3_error_repair.png"), dpi=200)
    plt.close(fig)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    groups = load_groups(BASE)
    plot_he_curves(groups)
    plot_ce_curves(groups)
    plot_cost(groups)
    plot_error_repair(groups)
    print(f"Figures saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
