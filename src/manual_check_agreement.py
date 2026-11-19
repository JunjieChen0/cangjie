"""检索相关性人工盲评与 LLM 判定的一致性（manual_check.csv × manual_check_key.csv）。

用法：python src/manual_check_agreement.py   # → results/retrieval_eval/manual_check_agreement.{md,json}

主结果用原始盲评分。敏感性分析是看过 LLM 分数后才提出的（事后），只作补充：
评分细则「1 = 主题相关但不能单独给出修复」若包括「只提到同一异常或类型」，则 POST_HOC_TO_1 这几条由 0 改为 1。
"""
from __future__ import annotations

import csv
import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "results", "retrieval_eval")
LEVELS = (0, 1, 2)
POST_HOC_TO_1 = (13, 20, 29)   # 片段只提到同一异常 / 类型（OverflowException、Rune、IndexOutOfBoundsException）


def load(path_human: str, path_key: str) -> tuple[list[int], list[int]]:
    """按编号对齐，返回 (人工分, LLM 分)。"""
    with open(path_human, encoding="utf-8-sig", newline="") as f:
        human = {int(r["no"]): int(r["human_score (0/1/2)"]) for r in csv.DictReader(f)}
    with open(path_key, encoding="utf-8-sig", newline="") as f:
        llm = {int(r["no"]): int(r["llm_score"]) for r in csv.DictReader(f)}
    if set(human) != set(llm):
        raise SystemExit("人工表与答案表的编号不一致")
    ids = sorted(human)
    return [human[i] for i in ids], [llm[i] for i in ids]


def kappa(a: list[int], b: list[int], quadratic: bool = False) -> float:
    """Cohen κ；quadratic=True 时为二次加权 κ。"""
    span = (LEVELS[-1] - LEVELS[0]) ** 2

    def w(i, j):
        return (i - j) ** 2 / span if quadratic else float(i != j)
    n, ca, cb = len(a), Counter(a), Counter(b)
    observed = sum(w(x, y) for x, y in zip(a, b)) / n
    expected = sum(w(i, j) * ca[i] * cb[j] for i in LEVELS for j in LEVELS) / n / n
    return 1 - observed / expected


def _ranks(x: list[int]) -> list[float]:
    order = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and x[order[j + 1]] == x[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1      # 并列取平均秩
        i = j + 1
    return r


def spearman(a: list[int], b: list[int]) -> float:
    ra, rb = _ranks(a), _ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    return cov / (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5


def agreement(human: list[int], llm: list[int]) -> dict:
    n = len(human)
    res = {"n": n, "exact": sum(h == m for h, m in zip(human, llm)),
           "within_1": sum(abs(h - m) <= 1 for h, m in zip(human, llm)),
           "kappa": round(kappa(human, llm), 3), "quadratic_kappa": round(kappa(human, llm, True), 3),
           "spearman": round(spearman(human, llm), 3),
           "human_higher": sum(h > m for h, m in zip(human, llm)),
           "llm_higher": sum(m > h for h, m in zip(human, llm)),
           "disagreements": [{"no": i, "human": h, "llm": m}
                             for i, (h, m) in enumerate(zip(human, llm), 1) if h != m]}
    for t in (1, 2):                              # ≥1：至少相关；=2：可直接修复
        hb, mb = [h >= t for h in human], [m >= t for m in llm]
        res[f"binary_ge{t}"] = {"agree": sum(x == y for x, y in zip(hb, mb)),
                                "human_pos": sum(hb), "llm_pos": sum(mb)}
    return res


def write_markdown(res: dict, path: str) -> None:
    p, s = res["primary"], res["sensitivity"]
    n = p["n"]
    rows = [("完全一致", f"{p['exact']}/{n}", f"{s['exact']}/{n}"),
            ("相差不超过 1 分", f"{p['within_1']}/{n}", f"{s['within_1']}/{n}"),
            ("未加权 Cohen κ", p["kappa"], s["kappa"]), ("二次加权 κ", p["quadratic_kappa"], s["quadratic_kappa"]),
            ("Spearman ρ", p["spearman"], s["spearman"]),
            ("≥1 分（至少相关）二分类一致", f"{p['binary_ge1']['agree']}/{n}", f"{s['binary_ge1']['agree']}/{n}"),
            ("=2 分（可直接修复）二分类一致", f"{p['binary_ge2']['agree']}/{n}", f"{s['binary_ge2']['agree']}/{n}")]
    dist = res["distribution"]
    md = ["# 检索相关性：人工盲评与 LLM 判定的一致性", "",
          f"样本：LLM 判定中按 2 / 1 / 0 分各抽 10 条、打乱顺序后由作者盲评（共 {n} 条，评分时未看 LLM 分数）。", "",
          f"分数分布（0 / 1 / 2）：人工 {dist['human']}，LLM {dist['llm']}。", "",
          "| 指标 | 主结果（原始盲评） | 敏感性分析（事后） |", "|---|---:|---:|"]
    md += [f"| {a} | {b} | {c} |" for a, b, c in rows]
    md += ["", f"不一致 {len(p['disagreements'])} 条，其中人工分高于 LLM 的 {p['human_higher']} 条、"
           f"低于 LLM 的 {p['llm_higher']} 条（LLM 判定偏宽松）："
           + "、".join(f"{d['no']}（人工 {d['human']} / LLM {d['llm']}）" for d in p["disagreements"]) + "。", "",
           f"=2 分：LLM 判了 {p['binary_ge2']['llm_pos']} 条，人工只给了 {p['binary_ge2']['human_pos']} 条，"
           "因此 hit@3 的绝对值应视为偏高的估计；各检索器由同一 LLM 判定，相互比较不受此影响。", "",
           f"敏感性分析：评分细则「1 = 主题相关但不能单独给出修复」若包括「只提到同一异常或类型」，"
           f"第 {'、'.join(map(str, POST_HOC_TO_1))} 条由 0 改为 1。该读法在看过 LLM 分数后才提出，只作补充，不作主结果。", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))


def main():
    human, llm = load(os.path.join(DIR, "manual_check.csv"), os.path.join(DIR, "manual_check_key.csv"))
    adjusted = [1 if i in POST_HOC_TO_1 and h == 0 else h for i, h in enumerate(human, 1)]
    res = {"distribution": {k: [Counter(v)[s] for s in LEVELS] for k, v in (("human", human), ("llm", llm))},
           "primary": agreement(human, llm), "post_hoc_to_1": list(POST_HOC_TO_1),
           "sensitivity": agreement(adjusted, llm)}
    with open(os.path.join(DIR, "manual_check_agreement.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    write_markdown(res, os.path.join(DIR, "manual_check_agreement.md"))
    p = res["primary"]
    print(f"完全一致 {p['exact']}/{p['n']}，κ={p['kappa']}，二次加权 κ={p['quadratic_kappa']}，ρ={p['spearman']}")


if __name__ == "__main__":
    main()
