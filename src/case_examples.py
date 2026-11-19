"""按固定规则从第 3 阶段原始结果中挑选典型修复案例，导出代码 diff 等素材供论文选用（不做人工挑选）。

用法：python src/case_examples.py      # → results/case_examples.md

挑选规则（Doubao-Seed-2.0-mini，direct 起点，3 次重复；第 0 轮共享，同一题在各组的起点代码相同）：
  1. hint 案例（HumanEval）：第 0 轮为 foreign_syntax 且至少匹配一条具体规则；raw 3 次都失败、hint 3 次都通过；
     取 hint 修复前后 diff 最短的一题。
  2. rag 案例（ClassEval，rag 的优势在类级任务上）：第 0 轮为 api_or_undeclared；raw 3 次都失败、rag 3 次都通过；
     同样取 diff 最短的一题。
  3. 规格歧义案例：ClassEval 第 53 题（题面写区分大小写，参考实现先转小写），给出 DeepSeek direct raw 第 1 次重复的末轮反馈。
"""
from __future__ import annotations

import difflib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import classify_error  # noqa: E402
from data import ROOT, load_classeval  # noqa: E402
from repair_hints import match_hints  # noqa: E402
from residual_failures import _LOCAL_PATH  # noqa: E402

RUNS = os.path.join(ROOT, "results", "stage3", "runs")
OUT = os.path.join(ROOT, "results", "case_examples.md")
REPS = (1, 2, 3)
GENERIC_HINT = "(no specific hint matched)"


def load_arm(prefix: str, base: str = RUNS) -> list[dict[str, dict]]:
    """[{题号: 记录}]，每次重复一个字典。"""
    out = []
    for r in REPS:
        with open(os.path.join(base, f"{prefix}_rep{r}.jsonl"), encoding="utf-8") as f:
            out.append({str(row["id"]): row for row in map(json.loads, f)})
    return out


def code_diff(before: str, after: str) -> list[str]:
    return list(difflib.unified_diff(before.splitlines(), after.splitlines(), "round 0", "repaired", lineterm="", n=1))


def has_specific_hint(feedback: str) -> bool:
    return any(GENERIC_HINT not in h for h in match_hints(feedback))


def pick(raw: list[dict], arm: list[dict], category: str, cond=lambda fb: True) -> tuple[str, list[str]] | None:
    """返回 (题号, diff)：第 0 轮属于 category 且满足 cond，raw 全部失败、arm 全部通过，diff 最短（同长取题号小者）。"""
    best = None
    for i in sorted(raw[0], key=int):
        hist0 = raw[0][i].get("history") or [{}]
        if classify_error(hist0[0]) != category or not cond(hist0[0].get("feedback", "")):
            continue
        if any(rep[i].get("passed") for rep in raw) or not all(rep[i].get("passed") for rep in arm):
            continue
        h = arm[0][i]["history"]
        d = code_diff(h[0]["code"], h[-1]["code"])
        if best is None or len(d) < len(best[1]):
            best = (i, d)
    return best


def strip_paths(text: str) -> str:
    """去掉形如 (C:\\Users\\...\\main.cj:3) 的本机临时路径，保留换行。"""
    return _LOCAL_PATH.sub("", text)


def _block(lang: str, text: str) -> list[str]:
    return [f"```{lang}", text.rstrip(), "```"]


def case_section(title: str, rule: str, raw: list[dict], arm: list[dict], picked, extra, bench: str) -> list[str]:
    if picked is None:
        return [f"## {title}", "", f"没有满足条件的题（{rule}）。", ""]
    i, diff = picked
    h0 = arm[0][i]["history"][0]
    L = [f"## {title}：{bench} 第 {i} 题", "", f"挑选规则：{rule}", "",
         f"raw 3 次重复的最终结果：{', '.join(rep[i]['history'][-1]['failure_kind'] for rep in raw)}；"
         f"该组第 1 次重复第 {len(arm[0][i]['history']) - 1} 轮通过。", "",
         "第 0 轮报错（节选）：", *_block("", strip_paths(h0["feedback"])[:800]), ""]
    return L + extra(h0) + ["", "修复前后代码 diff（该组第 1 次重复）：", *_block("diff", "\n".join(diff)), ""]


def hint_extra(h0: dict) -> list[str]:
    return ["hint 附加给模型的规则提示：", *_block("", "\n".join(match_hints(h0["feedback"])))]


def rag_extra(h0: dict) -> list[str]:
    return ["rag 检索到的文档片段（标题）：", *_block("", "\n".join(h0.get("retrieved", [])))]


def main():
    he_raw, he_hint = load_arm("doubao_mini_he_direct_raw"), load_arm("doubao_mini_he_direct_hint")
    ce_raw, ce_rag = load_arm("doubao_mini_ce_direct_raw"), load_arm("doubao_mini_ce_direct_rag")
    L = ["# 典型修复案例素材（自动挑选）", "", "数据：第 3 阶段 Doubao-Seed-2.0-mini，`direct` 起点，共享第 0 轮，3 次重复。", ""]
    L += case_section("案例 1：hint 修复外来语法",
                      "第 0 轮 foreign_syntax 且匹配到具体规则；raw 3/3 失败，hint 3/3 通过；diff 最短",
                      he_raw, he_hint, pick(he_raw, he_hint, "foreign_syntax", has_specific_hint), hint_extra,
                      "HumanEval")
    L += case_section("案例 2：rag 修复 API / 未声明标识符", "第 0 轮 api_or_undeclared；raw 3/3 失败，rag 3/3 通过；diff 最短",
                      ce_raw, ce_rag, pick(ce_raw, ce_rag, "api_or_undeclared"), rag_extra, "ClassEval")
    ce = load_classeval()["53"]
    ds = load_arm("ds_v41f_ce_direct_raw")[0]["53"]["history"][-1]
    stmt = [line.strip() for line in ce["prompt"].splitlines() if "case" in line.lower()]
    L += ["## 案例 3：规格歧义导致的残余失败（ClassEval 第 53 题）", "",
          "题面原文（含 case 的行）：", *_block("", "\n".join(stmt)), "",
          "参考实现在匹配前先把句子转成小写；测试 `test_find_longest_word_4` 要求 \"Apple is red.\" 匹配到 \"apple\"。",
          "DeepSeek direct raw 第 1 次重复的末轮反馈（修复反馈只给出失败的测试函数名）：",
          *_block("", strip_paths(ds["feedback"])[:600]), ""]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print(f"→ {OUT}")


if __name__ == "__main__":
    main()
