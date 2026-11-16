"""零成本实验：对已有生成结果做后处理（删除 main），再评测。

用法：python src/postprocess.py -i <solutions.jsonl> -o <out.jsonl>
然后：python src/evaluate.py -i <out.jsonl>
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import read_jsonl, write_jsonl  # noqa: E402
from llm import strip_main  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True)
ap.add_argument("-o", "--output", required=True)
a = ap.parse_args()
rows = read_jsonl(a.input)
changed = 0
for r in rows:
    new = strip_main(r["solution"])
    changed += new != r["solution"]
    r["solution"] = new
write_jsonl(a.output, rows)
print(f"{changed}/{len(rows)} solutions modified -> {a.output}")
