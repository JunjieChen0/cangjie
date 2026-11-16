"""从 CangjieBench 公开的评测记录（以及我们自己的结果）中挖掘高频 cjc 报错。

这一步不花一分钱：CangjieBench 的 Results/ 里已经保存了上千条失败样本的编译器输出。
产出：results/error_stats.csv（报错模板, 次数, 示例），用于
  1) 论文中的"错误分布"统计图
  2) 指导编写 repair_hints.py 的规则（优先覆盖 Top-20 报错）

用法：python src/mine_errors.py [--top 40]
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import BENCH_DIR, ROOT  # noqa: E402

ERR_LINE = re.compile(r"^error:\s*(.+)$", re.M)


KEYWORDS = set("""as break case catch class const continue do else enum extend false finally for from func
if import in init interface is let macro main match mut open operator override package private protected
public quote redef return spawn static struct super synchronized this throw true try type unsafe var where
while foreign inout prop sealed abstract unsafe Int64 Float64 String Bool Rune UInt8 Unit""".split())


def _mask(m: re.Match) -> str:
    tok = m.group(1)
    # 保留标点符号和关键字（它们正是"外来语法"的线索），只屏蔽用户标识符
    if not re.fullmatch(r"[A-Za-z_]\w*", tok) or tok in KEYWORDS:
        return f"'{tok}'"
    return "'<ID>'"


def normalize(msg: str) -> str:
    """把具体标识符替换成占位符，得到报错"模板"。"""
    msg = re.sub(r"'([^']*)'", _mask, msg)
    msg = re.sub(r"\b\d+\b", "<N>", msg)
    return msg.strip()


def iter_stderr(paths):
    for p in paths:
        with open(p, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if r.get("passed"):
                    continue
                if "run_result" in r:  # CangjieBench 格式
                    for s in (r["run_result"].get("stderr") or []):
                        if s:
                            yield p, s
                elif r.get("compile_stderr"):  # 本项目格式
                    yield p, r["compile_stderr"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=40)
    a = ap.parse_args()

    paths = glob.glob(os.path.join(BENCH_DIR, "Results", "**", "*HumanEval*.records.jsonl"), recursive=True)
    paths += glob.glob(os.path.join(ROOT, "results", "**", "*.records.jsonl"), recursive=True)
    cnt, example, samples = Counter(), {}, defaultdict(int)
    n_samples = 0
    for p, stderr in iter_stderr(paths):
        n_samples += 1
        seen = set()
        for m in ERR_LINE.findall(stderr):
            t = normalize(m)
            if t in seen:  # 同一样本内同类报错只计一次
                continue
            seen.add(t)
            cnt[t] += 1
            example.setdefault(t, m.strip())
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    out = os.path.join(ROOT, "results", "error_stats.csv")
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["template", "count", "example"])
        for t, c in cnt.most_common():
            w.writerow([t, c, example[t]])
    print(f"扫描 {len(paths)} 个记录文件，{n_samples} 个失败样本，{len(cnt)} 种报错模板 → {out}\n")
    for t, c in cnt.most_common(a.top):
        print(f"{c:5d}  {t[:110]}")


if __name__ == "__main__":
    main()
