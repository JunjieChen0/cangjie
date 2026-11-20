"""第 0 轮编译错误正则分类器（analyze.classify_error）的人工盲评复核。

用法：
  python src/classifier_check.py --export   # 抽样 → results/classifier_check/classifier_check.csv（盲评表）+ _key.csv（答案）
  python src/classifier_check.py            # 盲评填好后 → classifier_check_agreement.{md,json}

抽样：第 3 阶段与 Original-30 全部共享第 0 轮中的编译错误，按反馈文本去重后，按分类器给出的类别分层，
每类随机抽 PER_CLASS 条（不足则全取，seed 0），打乱顺序。评分规则见 docs/第0轮分类器人工复核.md。
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import classify_error  # noqa: E402
from residual_failures import _LOCAL_PATH  # noqa: E402

from data import ROOT  # noqa: E402

OUT = os.path.join(ROOT, "results", "classifier_check")
CATEGORIES = ("foreign_syntax", "api_or_undeclared", "type_or_mutability", "duplicate_main", "other_compile")
PER_CLASS = 15                     # 共享第 0 轮中没有 duplicate_main（实验去掉了 main），实际 4 类共 60 条
SEED = 0
MAX_CHARS = 1500
HUMAN_COL = "human_category"


def load_pool(root: str = ROOT) -> list[dict]:
    """[{source, id, feedback, predicted}]：编译错误的第 0 轮，按反馈文本去重（保留文件名与题号排序后的第一条）。"""
    seen, pool = set(), []
    for p in sorted(glob.glob(os.path.join(root, "results", "stage3", "r0", "*_r0.jsonl"))
                    + glob.glob(os.path.join(root, "results", "original30", "r0", "*_r0.jsonl"))):
        with open(p, encoding="utf-8") as f:
            for r in (json.loads(line) for line in f if line.strip()):
                h0 = (r.get("history") or [{}])[0]
                fb = h0.get("feedback", "")
                if h0.get("failure_kind") != "compile_error" or fb in seen:
                    continue
                seen.add(fb)
                pool.append({"source": os.path.basename(p)[: -len("_r0.jsonl")], "id": str(r["id"]),
                             "feedback": fb, "predicted": classify_error(h0)})
    return pool


def sample(pool: list[dict], per_class: int = PER_CLASS, seed: int = SEED) -> list[dict]:
    rng = random.Random(seed)
    picked = []
    for c in CATEGORIES:
        items = [x for x in pool if x["predicted"] == c]
        picked += rng.sample(items, min(per_class, len(items)))
    rng.shuffle(picked)                       # 打乱顺序，复核时看不出分类器给的类别
    return picked


def export(out: str = OUT) -> str:
    picked = sample(load_pool())
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "classifier_check.csv")
    with open(path, "w", encoding="utf-8-sig", newline="") as f, \
            open(os.path.join(out, "classifier_check_key.csv"), "w", encoding="utf-8-sig", newline="") as fk:
        w, wk = csv.writer(f), csv.writer(fk)
        w.writerow(["no", "feedback", HUMAN_COL, "note"])
        wk.writerow(["no", "source", "id", "predicted"])
        for n, x in enumerate(picked, 1):
            w.writerow([n, _LOCAL_PATH.sub("", x["feedback"])[:MAX_CHARS], "", ""])
            wk.writerow([n, x["source"], x["id"], x["predicted"]])
    return path


def cohen_kappa(a: list[str], b: list[str]) -> float:
    n, ca, cb = len(a), Counter(a), Counter(b)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum(ca[c] * cb[c] for c in set(a) | set(b)) / n / n
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def agreement(human: list[str], pred: list[str]) -> dict:
    per = {}
    for c in CATEGORIES:
        tp = sum(h == c and p == c for h, p in zip(human, pred))
        npred, nhuman = pred.count(c), human.count(c)
        per[c] = {"predicted": npred, "human": nhuman, "precision": round(tp / npred, 3) if npred else None,
                  "recall": round(tp / nhuman, 3) if nhuman else None}
    return {"n": len(human), "exact": sum(h == p for h, p in zip(human, pred)),
            "kappa": round(cohen_kappa(human, pred), 3), "per_class": per,
            "confusion": {f"{p} → {h}": k for (p, h), k in sorted(Counter(zip(pred, human)).items()) if p != h}}


def load_scored(out: str = OUT) -> tuple[list[str], list[str]]:
    with open(os.path.join(out, "classifier_check.csv"), encoding="utf-8-sig", newline="") as f:
        human = {int(r["no"]): r[HUMAN_COL].strip() for r in csv.DictReader(f)}
    with open(os.path.join(out, "classifier_check_key.csv"), encoding="utf-8-sig", newline="") as f:
        pred = {int(r["no"]): r["predicted"] for r in csv.DictReader(f)}
    bad = {i: v for i, v in human.items() if v not in CATEGORIES}
    if bad or set(human) != set(pred):
        raise SystemExit(f"盲评表未填完或类别名不合法：{dict(list(bad.items())[:5])}")
    ids = sorted(human)
    return [human[i] for i in ids], [pred[i] for i in ids]


def write_markdown(res: dict, path: str) -> None:
    md = ["# 第 0 轮编译错误分类器：人工盲评复核", "",
          f"共 {res['n']} 条（按分类器类别分层抽样，每类最多 {PER_CLASS} 条，评分时看不到分类器结果）。", "",
          f"完全一致 {res['exact']}/{res['n']}（{100 * res['exact'] / res['n']:.1f}%），Cohen κ = {res['kappa']}。", "",
          "| 类别 | 分类器判为 | 人工判为 | 精确率 | 召回率 |", "|---|---:|---:|---:|---:|"]
    for c, v in res["per_class"].items():
        md.append(f"| {c} | {v['predicted']} | {v['human']} | {v['precision'] if v['precision'] is not None else '—'} | "
                  f"{v['recall'] if v['recall'] is not None else '—'} |")
    md += ["", "不一致（分类器 → 人工：条数）：" + ("；".join(f"{k}：{v}" for k, v in res["confusion"].items()) or "无"), "",
           "注：分层抽样使各类别等量出现，精确率可直接解读；召回率与总体一致率受抽样比例影响，只作参考。", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", action="store_true", help="导出盲评表（会覆盖已有的表）")
    args = ap.parse_args()
    if args.export:
        print(f"→ {export()}")
        return
    res = agreement(*load_scored())
    with open(os.path.join(OUT, "classifier_check_agreement.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    write_markdown(res, os.path.join(OUT, "classifier_check_agreement.md"))
    print(f"完全一致 {res['exact']}/{res['n']}，κ={res['kappa']}")


if __name__ == "__main__":
    main()
