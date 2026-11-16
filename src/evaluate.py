"""评测一个 solutions jsonl（每行 {"id", "solution"}），输出 records 与 summary。

用法：
  # 自检：用官方参考答案跑一遍，应接近 100% 通过
  python src/evaluate.py --reference -o results/reference.jsonl
  # 评测某个生成结果
  python src/evaluate.py -i results/xxx.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import load_humaneval, read_jsonl, write_jsonl  # noqa: E402
from runner import compile_and_run  # noqa: E402

try:
    from tqdm import tqdm
except ImportError:  # tqdm 可选
    def tqdm(x, **k):
        return x


def evaluate_one(sol: dict, dataset: dict) -> dict:
    item = dataset[int(sol["id"])]
    res = compile_and_run(sol["solution"] + "\n" + item["test"])
    return {"id": item["id"], **res.to_dict()}


def evaluate(solutions: list[dict], workers: int = 4) -> tuple[list[dict], dict]:
    ds = load_humaneval()
    with ThreadPoolExecutor(workers) as ex:
        records = list(tqdm(ex.map(lambda s: evaluate_one(s, ds), solutions), total=len(solutions)))
    records.sort(key=lambda r: r["id"])
    n = len(records)
    kinds = Counter(r["failure_kind"] for r in records)
    summary = {
        "n": n,
        "pass@1": round(100 * kinds["passed"] / n, 2) if n else 0,
        "compile_rate": round(100 * (n - kinds["compile_error"]) / n, 2) if n else 0,
        "failure_kinds": dict(kinds),
    }
    return records, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", help="solutions jsonl")
    ap.add_argument("--reference", action="store_true", help="评测官方参考答案（环境自检）")
    ap.add_argument("-o", "--output", help="records 输出路径（默认 input + .records.jsonl）")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("-j", "--workers", type=int, default=4)
    a = ap.parse_args()

    if a.reference:
        sols = [{"id": d["id"], "solution": d["solution"]} for d in load_humaneval().values()]
        out = a.output or "results/reference.records.jsonl"
    else:
        sols = read_jsonl(a.input)
        out = a.output or a.input + ".records.jsonl"
    if a.limit:
        sols = sols[: a.limit]

    records, summary = evaluate(sols, a.workers)
    write_jsonl(out, records)
    with open(out.replace(".records.jsonl", "") + ".summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
