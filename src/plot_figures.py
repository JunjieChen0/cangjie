"""生成论文插图（输出到 results/figures/）：
1. fig1_rounds_curve.png   — 各模型 × 反馈模式的 Pass@1 随修复轮数（0–5）变化曲线
2. fig2_cost_pareto.png    — 总 Token 消耗 vs 最终 Pass@1（与 CangjieBench Agent 基线对比）
3. fig3_error_repair.png   — 按第 0 轮错误类别的修复成功率对比（blind / raw / hint）

用法：python src/plot_figures.py
"""
from __future__ import annotations

import glob
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import error_breakdown, load_exp, summarize_file  # noqa: E402
from data import ROOT  # noqa: E402

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT_DIR = os.path.join(ROOT, "results", "figures")


HE_GROUPS = [
    ("DeepSeek-V4.1-Flash", [
        ("ds_v41f_syntax_hint_r5", "Syntax + Hint", "-o", "#2ca02c"),
        ("ds_v41f_direct_hint_r5", "Direct + Hint", "-s", "#1f77b4"),
        ("ds_v41f_direct_raw_r5",  "Direct + Raw",  "--^", "#ff7f0e"),
        ("ds_v41f_direct_blind_r5","Direct + Blind",":x", "#7f7f7f"),
    ]),
    ("Doubao-Seed-2.0-Mini (轻量模型)", [
        ("doubao_mini_syntax_hint_r5",  "Syntax + Hint",  "-o", "#2ca02c"),
        ("doubao_mini_syntax_raw_r5",   "Syntax + Raw",   "--d", "#9467bd"),
        ("doubao_mini_direct_hint_r5",  "Direct + Hint",  "-s", "#1f77b4"),
        ("doubao_mini_direct_raw_r5",   "Direct + Raw",   "--^", "#ff7f0e"),
        ("doubao_mini_direct_blind_r5", "Direct + Blind", ":x", "#7f7f7f"),
    ]),
    ("Kimi-K3.1-Pro", [
        ("kimik31p_direct_hint_r5", "Direct + Hint", "-s", "#1f77b4"),
        ("kimik31p_direct_raw_r5",  "Direct + Raw",  "--^", "#ff7f0e"),
    ]),
]

CE_GROUPS = [
    ("DeepSeek-V4.1-Flash", [
        ("ds_v41f_ce_direct_hint_r5", "Direct + Hint", "-s", "#1f77b4"),
        ("ds_v41f_ce_direct_raw_r5",  "Direct + Raw",  "--^", "#ff7f0e"),
    ]),
    ("Doubao-Seed-2.0-Mini (轻量模型)", [
        ("doubao_mini_ce_syntax_hint_r5",  "Syntax + Hint",  "-o", "#2ca02c"),
        ("doubao_mini_ce_syntax_raw_r5",   "Syntax + Raw",   "--d", "#9467bd"),
        ("doubao_mini_ce_direct_hint_r5",  "Direct + Hint",  "-s", "#1f77b4"),
        ("doubao_mini_ce_direct_raw_r5",   "Direct + Raw",   "--^", "#ff7f0e"),
        ("doubao_mini_ce_direct_blind_r5", "Direct + Blind", ":x", "#7f7f7f"),
    ]),
]


def plot_curves(summaries: dict[str, dict], groups=HE_GROUPS,
                suptitle="不同反馈粒度下的多轮编译反馈修复曲线 (HumanEval-Cangjie, N=164)",
                filename="fig1_rounds_curve.png", doubao_legend_loc="center right"):
    fig, axes = plt.subplots(1, len(groups), figsize=(5.6 * len(groups), 4.6), sharey=True)
    xs = list(range(6))
    for ax, (title, items) in zip(axes, groups):
        for key, label, fmt, color in items:
            if key not in summaries:
                continue
            ys = summaries[key]["curve"]
            ax.plot(xs, ys, fmt, color=color, linewidth=2.0, markersize=6, label=f"{label} ({ys[-1]:.1f}%)")
        ax.set_title(title, fontsize=12)
        ax.set_xlabel("修复轮数 (Round)")
        ax.set_xticks(xs)
        ax.set_ylim(0, 105)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(loc=doubao_legend_loc if "Doubao" in title else "lower right", fontsize=9)
    axes[0].set_ylabel("Pass@1 (%)")
    fig.suptitle(suptitle, fontsize=13)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, filename), dpi=200)
    plt.close(fig)


def plot_pareto(summaries: dict[str, dict]):
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    labels = {
        "ds_v41f_syntax_hint_r5": ("DS-V4.1F Syntax+Hint", "#2ca02c", "o"),
        "ds_v41f_direct_hint_r5": ("DS-V4.1F Direct+Hint", "#1f77b4", "s"),
        "ds_v41f_direct_raw_r5":  ("DS-V4.1F Direct+Raw",  "#ff7f0e", "^"),
        "ds_v41f_direct_blind_r5":("DS-V4.1F Direct+Blind","#7f7f7f", "x"),
        "doubao_mini_syntax_hint_r5":  ("Doubao-Mini Syntax+Hint",  "#9467bd", "o"),
        "doubao_mini_syntax_raw_r5":   ("Doubao-Mini Syntax+Raw",   "#e377c2", "d"),
        "doubao_mini_direct_hint_r5":  ("Doubao-Mini Direct+Hint",  "#17becf", "s"),
        "doubao_mini_direct_raw_r5":   ("Doubao-Mini Direct+Raw",   "#bcbd22", "^"),
        "doubao_mini_direct_blind_r5": ("Doubao-Mini Direct+Blind", "#8c564b", "x"),
        "kimik31p_direct_hint_r5": ("Kimi-K3.1P Direct+Hint", "#d62728", "s"),
        "kimik31p_direct_raw_r5":  ("Kimi-K3.1P Direct+Raw",  "#ff9896", "^"),
    }
    for key, (lbl, col, mk) in labels.items():
        if key not in summaries:
            continue
        s = summaries[key]
        x = s["total_tokens"] / 1e6
        y = s["curve"][-1]
        ax.scatter(x, y, color=col, marker=mk, s=90, label=f"{lbl} ({x:.2f}M, {y:.1f}%)")
    ax.set_xlabel("总 Token 消耗（百万 tokens，N=164）")
    ax.set_ylabel("最终 Pass@1 (%)")
    ax.set_title("成本—效果对比：总 Token 消耗 vs 最终通过率")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="lower left", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig2_cost_pareto.png"), dpi=200)
    plt.close(fig)


def plot_error_repair(data: dict[str, list[dict]]):
    cats = ["foreign_syntax", "api_or_undeclared", "type_or_mutability", "test_failure"]
    cat_names = ["外来语法", "API/标识符缺失", "类型/可变性", "逻辑/测试失败"]
    targets = [
        ("doubao_mini_direct_blind_r5", "Doubao Blind", "#7f7f7f"),
        ("doubao_mini_direct_raw_r5",   "Doubao Raw",   "#ff7f0e"),
        ("doubao_mini_direct_hint_r5",  "Doubao Hint",  "#1f77b4"),
    ]
    avail = [(k, lbl, c) for k, lbl, c in targets if k in data]
    if not avail:
        return
    fig, ax = plt.subplots(figsize=(8.2, 4.5))
    w = 0.25
    xs = list(range(len(cats)))
    for idx, (key, lbl, col) in enumerate(avail):
        bd = error_breakdown(data[key])
        ys = [100 * bd[c][1] / bd[c][0] if c in bd and bd[c][0] > 0 else 0 for c in cats]
        pos = [x + (idx - (len(avail) - 1) / 2) * w for x in xs]
        bars = ax.bar(pos, ys, width=w, color=col, label=lbl)
        for b, y in zip(bars, ys):
            ax.text(b.get_x() + b.get_width() / 2, y + 1.5, f"{y:.0f}%", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(xs)
    ax.set_xticklabels(cat_names)
    ax.set_ylim(0, 110)
    ax.set_ylabel("修复成功率 (%)")
    ax.set_title("Doubao-Seed-2.0-Mini 按第 0 轮错误类别的修复成功率")
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig3_error_repair.png"), dpi=200)
    plt.close(fig)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    exp_dir = os.path.join(ROOT, "results", "exp")
    paths = sorted(p for p in glob.glob(os.path.join(exp_dir, "*.jsonl")) if not p.endswith(".records.jsonl"))
    summaries, data = {}, {}
    for p in paths:
        s = summarize_file(p)
        summaries[s["name"]] = s
        data[s["name"]] = load_exp(p)
    plot_curves(summaries)
    plot_curves(summaries, CE_GROUPS,
                "不同反馈粒度下的多轮编译反馈修复曲线 (ClassEval-Cangjie, N=84)",
                "fig4_rounds_curve_classeval.png", doubao_legend_loc="upper left")
    plot_pareto(summaries)
    plot_error_repair(data)
    print(f"Figures saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
