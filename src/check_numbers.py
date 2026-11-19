"""核对文档中的统计数字是否都能在 results/stats/*_stats.json 中找到。

用法：
  python src/check_numbers.py docs/实验汇总报告.md paper/main.tex

检查三类数字（其余数字不检查）：
- 带正负号的两位小数：差值与 95% CI（+16.67、−3.33、[+7.78, +26.67]），以及各组相对第 0 轮的提升（R5 均值 − R0）；
- 「均值 ± SD」：R5 均值 ± 标准差（44.44 ± 7.70，可带 %）；
- 4 位小数：p、p(Holm) 与逐次重复 McNemar p 值（0.0192）；「<0.0001」不检查。
找不到出处的数字连同行号列出，退出码为 1。来自其他实验（如第 2 阶段、pass@6）的数字也会被列出，需人工确认。
只支持纯文本（.md、.tex、.txt）；Word 文档请先另存为纯文本。
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIGNED = re.compile(r"(?<![\w.])([+\-−])(\d+\.\d{2})(?!\d)")
MEAN_SD = re.compile(r"(?<![\d.])(\d+\.\d{2})%?\s*±\s*(\d+\.\d{2})(?!\d)")
P_VALUE = re.compile(r"(?<![\d.<])0\.\d{4}(?!\d)")


def known_values(stats: list[dict]) -> dict[str, set]:
    """从统计 json 中收集可引用的数值：带号差值/CI、(均值, SD) 对、p 值。"""
    signed, mean_sd, p = set(), set(), set()
    for s in stats:
        for r in s.get("summary", []):
            mean_sd.add((round(r["r5_mean"], 2), round(r["r5_sd"], 2)))
            signed.add(round(round(r["r5_mean"], 2) - round(r["r0"], 2), 2))   # 相对第 0 轮的提升
        for r in s.get("comparisons", []) + s.get("sensitivity_excl_flaky", []):
            signed.update(round(r[k], 2) for k in ("diff", "ci_lo", "ci_hi") if k in r)
            p.update(round(x, 4) for x in [r.get("p"), r.get("p_holm"), *r.get("mcnemar_per_rep", [])]
                     if x is not None)
    return {"signed": signed, "mean_sd": mean_sd, "p": p}


def check_text(text: str, known: dict[str, set]) -> list[tuple[int, str]]:
    """返回找不到出处的数字 [(行号, 原文)]，按出现顺序。"""
    bad = []
    for no, line in enumerate(text.splitlines(), 1):
        found = []
        for m in SIGNED.finditer(line):
            v = float(m.group(2)) * (-1 if m.group(1) in "-−" else 1)
            if round(v, 2) not in known["signed"]:
                found.append((m.start(), m.group(0)))
        for m in MEAN_SD.finditer(line):
            if (float(m.group(1)), float(m.group(2))) not in known["mean_sd"]:
                found.append((m.start(), f"{m.group(1)} ± {m.group(2)}"))
        for m in P_VALUE.finditer(line):
            if round(float(m.group(0)), 4) not in known["p"]:
                found.append((m.start(), m.group(0)))
        bad += [(no, tok) for _, tok in sorted(found)]
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docs", nargs="+", help="要检查的文档（.md / .tex / .txt）")
    ap.add_argument("--stats", nargs="*", help="统计 json（默认 results/stats/*_stats.json）")
    args = ap.parse_args()
    paths = args.stats or sorted(glob.glob(os.path.join(ROOT, "results", "stats", "*_stats.json")))
    stats = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            stats.append(json.load(f))
    known = known_values(stats)
    n_bad = 0
    for doc in args.docs:
        if doc.lower().endswith(".docx"):
            sys.exit(f"{doc}：不支持 Word 文档，请先另存为纯文本")
        with open(doc, encoding="utf-8") as f:
            bad = check_text(f.read(), known)
        n_bad += len(bad)
        print(f"{doc}：{len(bad)} 个数字在统计文件中找不到")
        for no, tok in bad:
            print(f"  第 {no} 行：{tok}")
    sys.exit(1 if n_bad else 0)


if __name__ == "__main__":
    main()
