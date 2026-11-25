"""敏感性分析汇总：去掉判定不稳定的题（stage3_stats.FLAKY）和超时题后，各比较的结论是否改变。

只读各统计脚本已生成的 JSON（stage3 / original30 / review），不重新计算：
  python src/sensitivity_report.py     # → results/stats/sensitivity_report.{md,json}
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extra_stats import fmt_p  # noqa: E402
from review_stats import REVIEW_TIMEOUT_AS_FAIL  # noqa: E402
from stage3_stats import FLAKY  # noqa: E402

from data import ROOT  # noqa: E402

STATS = os.path.join(ROOT, "results", "stats")
ALPHA = 0.05
SOURCES = (("stage3", "第 3 阶段（33 个预先设定的比较）"), ("original30", "Original-30（17 个预先设定的比较）"),
           ("review", "补充实验（族 G / A / R，各族内 Holm）"))


def flips(comps: list[dict], sens: list[dict]) -> list[dict]:
    """逐个比较对照全部题与去掉后的结果，返回显著性改变或差值方向改变的比较。"""
    out = []
    for r, s in zip(comps, sens):
        sig_a, sig_b = r["p_holm"] < ALPHA, s["p_holm"] < ALPHA
        if sig_a != sig_b or (r["diff"] * s["diff"] < 0):
            out.append({k: r.get(k) for k in ("family", "model", "ds", "prompt", "a", "b")} |
                       {"diff_all": r["diff"], "p_holm_all": r["p_holm"], "n_after": s["n"],
                        "diff_after": s["diff"], "p_holm_after": s["p_holm"]})
    return out


def section(stats: dict) -> dict:
    comps, sens = stats["comparisons"], stats["sensitivity_excl_flaky"]
    shifts = [abs(r["diff"] - s["diff"]) for r, s in zip(comps, sens)]
    return {"comparisons": len(comps),
            "significant_all": sum(r["p_holm"] < ALPHA for r in comps),
            "significant_after": sum(s["p_holm"] < ALPHA for s in sens),
            "max_abs_diff_shift": round(max(shifts), 2) if shifts else None,
            "changed": flips(comps, sens),
            "timeouts": [{k: r[k] for k in ("model", "ds", "prompt", "feedback", "reps", "timeouts")}
                         for r in stats.get("summary", []) if r.get("timeouts")]}


def write_markdown(res: dict, path: str) -> None:
    L = ["# 敏感性分析汇总：判定不稳定的题与超时题（自动生成）", "",
         "去掉的题：" + "；".join(f"{ds} 第 {', '.join(sorted(ids))} 题" for ds, ids in sorted(FLAKY.items()))
         + "（参考答案重复运行时判定不稳定，原因见 stage3_stats.py 中 FLAKY 的注释）；"
         "并且每个比较中，两组任一次重复里 API 超时的题从两组同时去掉（超时只出现在 "
         + "、".join(sorted(REVIEW_TIMEOUT_AS_FAIL)) + "，主分析中按未通过计入分母，不过滤）。", "",
         f"「结论改变」= Holm 校正后的显著性（α = {ALPHA}）改变，或差值正负号改变。", ""]
    for key, title in SOURCES:
        s = res.get(key)
        L += [f"## {title}", ""]
        if s is None:
            L += ["（尚无统计结果）", ""]
            continue
        L += [f"比较 {s['comparisons']} 个；Holm 显著：全部题 {s['significant_all']} 个 → 去掉后 {s['significant_after']} 个；"
              f"差值最大变化 {s['max_abs_diff_shift']} 个百分点。", ""]
        if s["changed"]:
            L += ["| 族 | 模型 | 数据集 | 起点 | A vs B | 差值 / p(Holm)（全部题） | 题数（去掉后） | 差值 / p(Holm)（去掉后） |",
                  "|---|---|---|---|---|---|---|---|"]
            L += [f"| {c['family'] or '—'} | {c['model']} | {c['ds']} | {c['prompt']} | {c['a']} vs {c['b']} | "
                  f"{c['diff_all']:+.2f} / {fmt_p(c['p_holm_all'])} | {c['n_after']} | "
                  f"{c['diff_after']:+.2f} / {fmt_p(c['p_holm_after'])} |" for c in s["changed"]]
        else:
            L.append("没有比较的结论发生改变。")
        if s["timeouts"]:
            L += ["", "超时（按未通过计入主分析）：" + "；".join(
                f"{t['model']} {t['ds']} {t['prompt']} {t['feedback']}：{t['timeouts']} 题次（{t['reps']} 次重复合计）"
                for t in s["timeouts"]) + "。"]
        L.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def main():
    res = {}
    for key, _ in SOURCES:
        p = os.path.join(STATS, f"{key}_stats.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                res[key] = section(json.load(f))
    with open(os.path.join(STATS, "sensitivity_report.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    write_markdown(res, os.path.join(STATS, "sensitivity_report.md"))
    for key, s in res.items():
        print(f"{key}: {s['comparisons']} 个比较，结论改变 {len(s['changed'])} 个")


if __name__ == "__main__":
    main()
