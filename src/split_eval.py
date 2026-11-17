"""5:5 题目划分防过拟合验证（Held-out Split Validation）。

1. 按固定随机种子（seed=42）将 HumanEval 164 题划分为 Dev(82) / Test(82)
2. 统计已有全量实验在 Dev vs Test 两半上的表现是否一致（零成本）
3. 检验：如果仅用 Dev 82 题的 CangjieBench 公开报错来触发 repair_hints.py 中的规则，
   哪些规则在 Dev 中高频出现，哪些仅出现在 Test 中。
"""
from __future__ import annotations

import glob
import json
import os
import random
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import load_exp, round_passed  # noqa: E402
from data import BENCH_DIR, ROOT  # noqa: E402
from repair_hints import RULES  # noqa: E402


def get_split(seed: int = 42) -> tuple[set[int], set[int]]:
    ids = list(range(164))
    random.Random(seed).shuffle(ids)
    return set(ids[:82]), set(ids[82:])


def dev_supported_rules(dev_ids: set[int], min_hits: int = 5) -> list[str]:
    """统计 CangjieBench 公开失败样本中，仅看 Dev 82 题时每条规则命中多少次。"""
    paths = glob.glob(os.path.join(BENCH_DIR, "Results", "**", "*HumanEval*.records.jsonl"), recursive=True)
    hits = Counter()
    for p in paths:
        with open(p, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if r.get("passed") or r.get("id") not in dev_ids:
                    continue
                stderr = "\n".join(s for s in (r.get("run_result", {}).get("stderr") or []) if s)
                for name, pat, _ in RULES:
                    if re.search(pat, stderr, re.I):
                        hits[name] += 1
    print("=== Dev 82 题中各规则在公开失败样本中的命中次数 ===")
    kept = []
    for name, _, _ in RULES:
        c = hits[name]
        mark = "KEEP" if c >= min_hits else "DROP"
        print(f"  {name:26s}: {c:4d}  [{mark}]")
        if c >= min_hits:
            kept.append(name)
    return kept


def main():
    dev_ids, test_ids = get_split(42)
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    with open(os.path.join(ROOT, "results", "split_seed42.json"), "w", encoding="utf-8") as f:
        json.dump({"seed": 42, "dev": sorted(dev_ids), "test": sorted(test_ids)}, f, indent=2)

    dev_supported_rules(dev_ids, min_hits=5)

    print("\n=== 已有实验在 Dev(82) vs Test(82) 上的 Pass@1 对比 ===")
    print(f"{'实验':32s} | {'Dev R0':>6s} {'Dev R5':>6s} | {'Test R0':>7s} {'Test R5':>7s}")
    print("-" * 74)
    for name in [
        "doubao_mini_direct_blind_r5",
        "doubao_mini_direct_raw_r5",
        "doubao_mini_direct_hint_r5",
        "doubao_mini_syntax_raw_r5",
        "doubao_mini_syntax_hint_r5",
        "ds_v41f_direct_raw_r5",
        "ds_v41f_direct_hint_r5",
    ]:
        p = os.path.join(ROOT, "results", "exp", f"{name}.jsonl")
        if not os.path.exists(p):
            continue
        rows = load_exp(p)
        d_rows = [r for r in rows if r["id"] in dev_ids]
        t_rows = [r for r in rows if r["id"] in test_ids]
        dr0 = 100 * sum(1 for r in d_rows if round_passed(r, 0)) / len(d_rows)
        dr5 = 100 * sum(1 for r in d_rows if round_passed(r, 5)) / len(d_rows)
        tr0 = 100 * sum(1 for r in t_rows if round_passed(r, 0)) / len(t_rows)
        tr5 = 100 * sum(1 for r in t_rows if round_passed(r, 5)) / len(t_rows)
        print(f"{name:32s} | {dr0:5.2f}% {dr5:5.2f}% |  {tr0:5.2f}%  {tr5:5.2f}%")


if __name__ == "__main__":
    main()
