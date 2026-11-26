"""扩展实验（族 G / A / R / I）的事后稳健性检查（看过主结果之后补做，不改变主分析的判定）。

1. 置换次数：主分析的符号翻转检验用 10,000 次（方案第二节），p 值最小约 1e-4；这里改用 100,000 次重算全部比较与交互，
   检查族内 Holm 后的显著性是否随蒙特卡罗精度改变。
2. 已知缺陷题：在现有敏感性分析（HumanEval 20、ClassEval 58 与超时题）之外，另把论文中记录的两道基准缺陷题
   ClassEval 48（参考答案在部分环境下编译失败）与 ClassEval 53（测试与题面的大小写要求矛盾）一并去掉，
   分别用 10,000 次（与主分析同口径）和 100,000 次置换重算。

10 万次置换用 numpy 的 PCG64 原始随机流取符号，差值放大为整数后再求和，结果与平台和 numpy 版本无关。
主分析结果读自 results/stats/review_stats.json（须先运行 review_stats.py）；只读结果文件，不调用 API：
  python src/robustness_checks.py     # → results/stats/robustness_checks.{md,json}
"""
from __future__ import annotations

import contextlib
import json
import os
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import review_stats as R  # noqa: E402
import stage3_stats as S  # noqa: E402
from extra_stats import fmt_p  # noqa: E402

N_PERM_HI = 100_000
CHUNK = 10_000
SCALE = 60            # 每题差值是 1～5 次重复均值之差，乘 60 后为整数
ALPHA = 0.05
DEFECTIVE = {"he": S.FLAKY["he"], "ce": S.FLAKY["ce"] | frozenset({"48", "53"})}
OUT = os.path.join(R.RESULTS, "stats")


def sign_flip_p_hi(diffs: list[float], n_perm: int = N_PERM_HI, seed: int = 0) -> float:
    """与 stage3_stats.sign_flip_p 同一检验（双侧，(hits + 1) / (n + 1)），随机符号取自 PCG64 原始流的最低位。"""
    scaled = [round(d * SCALE) for d in diffs]
    if any(abs(d * SCALE - s) > 1e-6 for d, s in zip(diffs, scaled)):
        raise ValueError("差值不是 1/60 的整数倍，不能精确放大")
    v = np.array([s for s in scaled if s != 0], dtype=np.int64)
    obs = abs(int(v.sum()))
    if obs == 0:
        return 1.0
    bitgen, hits, left = np.random.PCG64(seed), 0, n_perm
    while left:
        k = min(left, CHUNK)
        signs = 1 - 2 * (bitgen.random_raw(k * len(v)) & 1).astype(np.int64).reshape(k, len(v))
        hits += int((np.abs(signs @ v) >= obs).sum())
        left -= k
    return (hits + 1) / (n_perm + 1)


@contextlib.contextmanager
def permutation_test(fn):
    """临时替换 stage3_stats.compare 与 review_stats.interaction 所用的检验函数。"""
    old = S.sign_flip_p, R.sign_flip_p
    S.sign_flip_p = R.sign_flip_p = fn
    try:
        yield
    finally:
        S.sign_flip_p, R.sign_flip_p = old


def _key(r: dict) -> tuple:
    return tuple(r.get(k) for k in ("family", "model", "ds", "prompt", "a", "b"))


def contrast(main: list[dict], alt: list[dict]) -> dict:
    """alt 与主分析逐个比较：各族显著数、显著性改变或差值变号的比较、差值最大变化。"""
    base = {_key(r): r for r in main}
    changed = []
    for r in alt:
        m = base[_key(r)]
        if (m["p_holm"] < ALPHA) != (r["p_holm"] < ALPHA) or m["diff"] * r["diff"] < 0:
            changed.append({k: r.get(k) for k in ("family", "model", "ds", "prompt", "a", "b")} |
                           {"diff_main": m["diff"], "p_holm_main": m["p_holm"], "n_main": m["n"],
                            "diff_alt": r["diff"], "p_holm_alt": r["p_holm"], "n_alt": r["n"]})
    return {"significant_main": dict(Counter(r["family"] for r in main if r["p_holm"] < ALPHA)),
            "significant_alt": dict(Counter(r["family"] for r in alt if r["p_holm"] < ALPHA)),
            "max_abs_diff_shift": round(max(abs(r["diff"] - base[_key(r)]["diff"]) for r in alt), 2),
            "changed": changed}


def run() -> dict:
    with open(os.path.join(OUT, "review_stats.json"), encoding="utf-8") as f:
        stats = json.load(f)
    main, inter = stats["comparisons"], stats["interaction"]
    review, olds = R.bases(False)
    groups = R.load_all(review, olds, S.N_TASKS)
    defects_10k = R.run_families(groups, exclude=DEFECTIVE)
    with permutation_test(sign_flip_p_hi):
        hi, inter_hi = R.run_families(groups), R.interaction(groups)
        defects_hi = R.run_families(groups, exclude=DEFECTIVE)
    ikey = {(r["family"], r["model"], r["ds"]): r for r in inter_hi}
    return {"n_perm_main": S.N_PERM, "n_perm_hi": N_PERM_HI,
            "defective_tasks": {ds: sorted(ids, key=int) for ds, ids in DEFECTIVE.items()},
            "perm_100k": contrast(main, hi),
            "defects_10k": contrast(main, defects_10k),
            "defects_100k": contrast(main, defects_hi),
            "interaction": [{k: r[k] for k in ("family", "model", "ds", "n", "interaction")} |
                            {"p_holm_main": r["p_holm"],
                             "p_holm_100k": ikey[(r["family"], r["model"], r["ds"])]["p_holm"]} for r in inter]}


def _counts(d: dict) -> str:
    return "、".join(f"{f} {d.get(f, 0)}" for f in ("G", "A", "R")) + f"，合计 {sum(d.values())}"


def write_markdown(res: dict, path: str) -> None:
    ex = "；".join(f"{ds} 第 {', '.join(ids)} 题" for ds, ids in sorted(res["defective_tasks"].items()))
    L = ["# 扩展实验的事后稳健性检查（自动生成）", "",
         "看过主结果之后补做，不改变主分析的判定（主分析见 review_stats.md）。「结论改变」= 族内 Holm 后的显著性"
         f"（α = {ALPHA}）改变，或差值正负号改变；对照对象都是主分析（全部题，{res['n_perm_main']:,} 次置换）。", ""]
    sections = (("perm_100k", f"置换 {res['n_perm_hi']:,} 次（全部题）"),
                ("defects_10k", f"去掉已知缺陷题，置换 {res['n_perm_main']:,} 次"),
                ("defects_100k", f"去掉已知缺陷题，置换 {res['n_perm_hi']:,} 次"))
    for key, title in sections:
        s = res[key]
        L += [f"## {title}", "", f"Holm 显著：主分析 {_counts(s['significant_main'])} → {_counts(s['significant_alt'])}；"
              f"差值最大变化 {s['max_abs_diff_shift']} 个百分点。", ""]
        if key.startswith("defects"):
            L += [f"去掉的题：{ex}（不去掉超时题）。", ""]
        L += ["| 族 | 模型 | 数据集 | 起点 | A vs B | 差值 / p(Holm)（主分析） | 题数 | 差值 / p(Holm)（本检查） |",
              "|---|---|---|---|---|---|---:|---|"]
        L += [f"| {c['family']} | {c['model']} | {c['ds']} | {c['prompt']} | {c['a']} vs {c['b']} | "
              f"{c['diff_main']:+.2f} / {fmt_p(c['p_holm_main'])} | {c['n_alt']} | "
              f"{c['diff_alt']:+.2f} / {fmt_p(c['p_holm_alt'])} |" for c in s["changed"]] or ["（没有比较的结论改变）"]
        L.append("")
    L += [f"## syntax × hint 交互（置换 {res['n_perm_hi']:,} 次）", "",
          "| 族 | 模型 | 数据集 | 题数 | 交互 | p(Holm)（主分析） | p(Holm)（10 万次） |", "|---|---|---|---:|---:|---|---|"]
    L += [f"| {r['family']} | {r['model']} | {r['ds']} | {r['n']} | {r['interaction']:+.2f} | "
          f"{fmt_p(r['p_holm_main'])} | {fmt_p(r['p_holm_100k'])} |" for r in res["interaction"]]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main():
    res = run()
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "robustness_checks.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    write_markdown(res, os.path.join(OUT, "robustness_checks.md"))
    for key in ("perm_100k", "defects_10k", "defects_100k"):
        s = res[key]
        print(f"{key}: 显著 {sum(s['significant_main'].values())} → {sum(s['significant_alt'].values())}，"
              f"结论改变 {len(s['changed'])} 个")


if __name__ == "__main__":
    main()
