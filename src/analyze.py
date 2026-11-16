"""实验结果统计、McNemar 显著性检验与错误类别修复率分析。

用法：
  python src/analyze.py
"""
from __future__ import annotations

import glob
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import ROOT  # noqa: E402


def load_exp(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def round_passed(row: dict, k: int) -> bool:
    return bool(row.get("passed")) and row.get("rounds_used", 99) <= k


def mcnemar_p(rows_a: list[dict], rows_b: list[dict], k: int) -> tuple[int, int, float]:
    """精确 McNemar 双侧检验（二项分布），返回 (a_only, b_only, p_value)。"""
    ma = {r["id"]: round_passed(r, k) for r in rows_a}
    mb = {r["id"]: round_passed(r, k) for r in rows_b}
    common = set(ma) & set(mb)
    b = sum(1 for i in common if ma[i] and not mb[i])  # A 过 B 没过
    c = sum(1 for i in common if not ma[i] and mb[i])  # B 过 A 没过
    n = b + c
    if n == 0:
        return b, c, 1.0
    m = min(b, c)
    p = 2.0 * sum(math.comb(n, i) for i in range(m + 1)) / (2 ** n)
    return b, c, min(1.0, p)


def classify_error(hist0: dict) -> str:
    """对第 0 轮失败进行细粒度归类（用于 RQ4）。"""
    kind = hist0.get("failure_kind", "")
    if kind == "passed":
        return "passed"
    if kind in ("test_failure", "runtime_exception", "timeout", "nonzero_exit"):
        return kind
    fb = hist0.get("feedback", "")
    if re.search(r"multiple 'main'|overload conflicts", fb, re.I):
        return "duplicate_main"
    if re.search(r"is not a member of|undeclared (identifier|type name)|can not find package", fb, re.I):
        return "api_or_undeclared"
    if re.search(r"mismatched types|type incompatible|cannot assign to immutable|invalid binary operator|no matching function", fb, re.I):
        return "type_or_mutability"
    if re.search(r"expected |unexpected token|unclosed delimiter|unknown suffix", fb, re.I):
        return "foreign_syntax"
    return "other_compile"


def summarize_file(path: str) -> dict:
    rows = load_exp(path)
    n = len(rows)
    curve = [round(100 * sum(1 for r in rows if round_passed(r, k)) / n, 2) for k in range(6)]
    r0_comp = sum(1 for r in rows if r.get("history") and r["history"][0]["failure_kind"] != "compile_error")
    pt = sum(r.get("usage", {}).get("prompt_tokens", 0) for r in rows)
    ct = sum(r.get("usage", {}).get("completion_tokens", 0) for r in rows)
    fail0 = [r for r in rows if r.get("history") and r["history"][0]["failure_kind"] != "passed"]
    fixed = [r for r in fail0 if r.get("passed")]
    avg_rnd = round(sum(r["rounds_used"] for r in fixed) / len(fixed), 2) if fixed else 0.0
    return {
        "name": os.path.basename(path).replace(".jsonl", ""),
        "n": n,
        "r0_compile": round(100 * r0_comp / n, 2),
        "curve": curve,
        "fail0": len(fail0),
        "fixed": len(fixed),
        "avg_rnd_fixed": avg_rnd,
        "prompt_tokens": pt,
        "completion_tokens": ct,
        "total_tokens": pt + ct,
    }


def error_breakdown(rows: list[dict]) -> dict[str, tuple[int, int]]:
    """返回 {error_cat: (total_at_r0, fixed_after_repair)}"""
    tot, fix = Counter(), Counter()
    for r in rows:
        if not r.get("history"):
            continue
        cat = classify_error(r["history"][0])
        if cat == "passed":
            continue
        tot[cat] += 1
        if r.get("passed"):
            fix[cat] += 1
    return {k: (tot[k], fix[k]) for k in sorted(tot, key=lambda x: -tot[x])}


def main():
    exp_dir = os.path.join(ROOT, "results", "exp")
    paths = sorted(p for p in glob.glob(os.path.join(exp_dir, "*.jsonl")) if not p.endswith(".records.jsonl"))
    if not paths:
        print("No experiment files found in results/exp/")
        return

    print("=== 1. 实验总表 ===")
    print(f"{'实验名称':34s} | {'N':>3s} | {'R0编译':>6s} | {'R0':>6s} {'R1':>6s} {'R2':>6s} {'R3':>6s} {'R4':>6s} {'R5':>6s} | {'均轮':>4s} | {'总Token':>9s}")
    print("-" * 118)
    data = {}
    for p in paths:
        s = summarize_file(p)
        data[s["name"]] = load_exp(p)
        c = " ".join(f"{v:5.2f}%" for v in s["curve"])
        print(f"{s['name']:34s} | {s['n']:3d} | {s['r0_compile']:5.2f}% | {c} | {s['avg_rnd_fixed']:4.2f} | {s['total_tokens']:9,d}")

    print("\n=== 2. 类别修复成功率（RQ4） ===")
    for name, rows in data.items():
        bd = error_breakdown(rows)
        parts = [f"{k}: {fx}/{tt}({100*fx/tt:.0f}%)" for k, (tt, fx) in bd.items()]
        print(f"[{name}] " + " | ".join(parts))

    print("\n=== 3. 成对 McNemar 检验 ===")
    by_prefix = defaultdict(dict)
    for name, rows in data.items():
        m = re.match(r"^(.+)_(blind|raw|hint)_r\d+$", name)
        if m:
            by_prefix[m.group(1)][m.group(2)] = rows
    for prefix, grp in sorted(by_prefix.items()):
        for a, b in [("hint", "raw"), ("hint", "blind"), ("raw", "blind")]:
            if a in grp and b in grp:
                for k in (1, 2, 3, 5):
                    ca, cb, pv = mcnemar_p(grp[a], grp[b], k)
                    sig = "*" if pv < 0.05 else ""
                    print(f"  {prefix} | R{k} {a} vs {b}: {a}_only={ca}, {b}_only={cb}, p={pv:.4f} {sig}")


if __name__ == "__main__":
    main()
