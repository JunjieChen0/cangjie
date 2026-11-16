"""加载 CangjieBench 数据集（HumanEval 子集）。"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH_DIR = os.path.join(ROOT, "external", "CangjieBench")
HUMANEVAL = os.path.join(BENCH_DIR, "CangjieBench", "HumanEval_Cangjie.jsonl")
CLASSEVAL = os.path.join(BENCH_DIR, "CangjieBench", "ClassEval_Cangjie.jsonl")
SYNTAX_RULE = os.path.join(BENCH_DIR, "Prompts", "syntax_rule.md")


def read_jsonl(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: str, rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_humaneval() -> dict[int, dict]:
    """返回 {id: {"id","prompt","solution","test"}}"""
    return {d["id"]: d for d in read_jsonl(HUMANEVAL)}


def load_classeval() -> dict[int, dict]:
    """返回 ClassEval 84 题（取集成测试 test[-1]）。"""
    out = {}
    for d in read_jsonl(CLASSEVAL):
        t = d["test"][-1] if isinstance(d["test"], list) else d["test"]
        out[d["id"]] = {"id": d["id"], "prompt": d["prompt"], "solution": d["solution"], "test": t}
    return out


def load_syntax_rule() -> str:
    with open(SYNTAX_RULE, encoding="utf-8") as f:
        return f.read()
