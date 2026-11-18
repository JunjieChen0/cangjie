"""生成 + 编译反馈迭代修复（本项目的核心实验脚本）。

流程（每道题）：
  第 0 轮：用 direct 或 syntax 提示生成代码 → 编译运行
  第 k 轮：若失败，把报错按 --feedback 模式喂回模型 → 重新生成 → 编译运行
  直到通过或达到 --rounds 上限。记录每一轮的结果与 token 用量。

用法示例：
  set LLM_BASE_URL=https://api.deepseek.com/v1
  set LLM_API_KEY=sk-xxx
  set LLM_MODEL=deepseek-chat
  python src/repair.py --prompt syntax --feedback raw --rounds 3 --limit 10 -o results/ds_syntax_raw_r3.jsonl

  # 不调 API、直接从 CangjieBench 已公开的失败结果开始修复（省掉第 0 轮的钱）：
  python src/repair.py --init external/CangjieBench/Results/Text_to_Code/Syntax_Constrained/DeepSeek-V3_HumanEval.jsonl ...
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prompts as P  # noqa: E402
from data import load_classeval, load_humaneval, load_original30, load_syntax_rule, read_jsonl, write_jsonl  # noqa: E402
from doc_retrieval import format_docs, retrieve_for_feedback  # noqa: E402
from llm import chat, extract_code, strip_main  # noqa: E402
from reeval_classeval import load_classeval_tests  # noqa: E402
from repair_hints import match_hints  # noqa: E402
from runner import compile_and_run, compile_only  # noqa: E402

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, **k):
        return x


def first_prompt(item: dict, mode: str, syntax_rule: str) -> str:
    if mode == "direct":
        return P.DIRECT.format(question=item["prompt"])
    return P.SYNTAX.format(syntax_rule=syntax_rule, question=item["prompt"])


FEEDBACK_CAP = 3000  # 与 runner.RunResult.feedback 的截断长度一致


@dataclass
class TestsResult:
    """--all-tests 模式下一轮的汇总结果（与 RunResult 一样提供 passed / failure_kind / feedback）。"""
    passed: bool
    failure_kind: str
    feedback: str
    status: list[bool]


def aggregate_feedback(results: list) -> TestsResult:
    """把同一份代码分别跑每个测试的结果合并成一条反馈。

    有编译错误时只报编译错误（相同报错去重）；否则按顺序列出失败的测试。总长截断到 FEEDBACK_CAP。
    """
    status = [r.passed for r in results]
    if all(status):
        return TestsResult(True, "passed", "", status)
    compile_errs = [(i, r) for i, r in enumerate(results) if r.failure_kind == "compile_error"]
    if compile_errs:
        seen, parts = set(), []
        for i, r in compile_errs:
            if r.feedback not in seen:
                seen.add(r.feedback)
                parts.append((i, r.feedback))
        if len(parts) == 1:
            text = parts[0][1]
        else:
            text = "\n\n".join(f"[with test #{i}]\n{fb}" for i, fb in parts)
        return TestsResult(False, "compile_error", text[:FEEDBACK_CAP], status)
    failed = [(i, r) for i, r in enumerate(results) if not r.passed]
    text = "\n\n".join(f"[test #{i} {r.failure_kind}]\n{r.feedback}" for i, r in failed)
    head = f"{len(failed)} of {len(results)} tests failed.\n\n"
    return TestsResult(False, failed[0][1].failure_kind, (head + text)[:FEEDBACK_CAP], status)


def evaluate(code: str, item: dict, all_tests: bool):
    if all_tests:
        return aggregate_feedback([compile_and_run(code + "\n" + t) for t in item["tests"]])
    return compile_and_run(code + "\n" + item["test"])


def repair_prompt(res, mode: str) -> tuple[str, dict]:
    """返回 (修复提示, 需记入 history 的附加信息)。"""
    if mode == "blind":
        return P.REPAIR_BLIND, {}
    if mode == "raw":
        return P.REPAIR_RAW.format(kind=res.failure_kind, feedback=res.feedback), {}
    if mode == "hint":
        hints = "\n".join(match_hints(res.feedback))
        return P.REPAIR_HINT.format(kind=res.failure_kind, feedback=res.feedback, hints=hints), {}
    if mode == "rag":
        chunks = retrieve_for_feedback(res.feedback)
        return (P.REPAIR_RAG.format(kind=res.failure_kind, feedback=res.feedback, docs=format_docs(chunks)),
                {"retrieved": [c["title"] for c in chunks]})
    raise ValueError(mode)


def solve(item: dict, args, syntax_rule: str, init_code: str | None) -> dict:
    messages = [{"role": "system", "content": P.SYSTEM}]
    history, usage_total = [], {"prompt_tokens": 0, "completion_tokens": 0}
    temps_used: set[float] = set()

    def post(code: str) -> str:
        return strip_main(code) if args.strip_main else code

    def ask() -> str:
        reply, u = chat(messages, model=args.model, temperature=args.temperature)
        messages.append({"role": "assistant", "content": reply})
        for k in usage_total:
            usage_total[k] += u[k]
        temps_used.add(u.get("temperature", args.temperature))
        return post(extract_code(reply))

    def record(rnd: int, res, code: str) -> None:
        entry = {"round": rnd, "failure_kind": res.failure_kind, "feedback": res.feedback[:1500], "code": code}
        if isinstance(res, TestsResult):
            entry["status"] = res.status
        history.append(entry)

    messages.append({"role": "user", "content": first_prompt(item, args.prompt, syntax_rule)})
    if init_code is not None:  # 复用已有的第 0 轮结果
        code = post(init_code)
        messages.append({"role": "assistant", "content": f"```cangjie\n{init_code}\n```"})
    else:
        code = ask()

    for rnd in range(args.rounds + 1):
        if args.compile_only_feedback:
            comp_res = compile_only(code)
            if comp_res.passed or rnd == args.rounds:
                record(rnd, evaluate(code, item, args.all_tests), code)
                break
            res = comp_res
            record(rnd, res, code)
        else:
            res = evaluate(code, item, args.all_tests)
            record(rnd, res, code)
            if res.passed or rnd == args.rounds:
                break
        prompt, meta = repair_prompt(res, args.feedback)
        history[-1].update(meta)
        messages.append({"role": "user", "content": prompt})
        code = ask()

    return {"id": item["id"], "passed": history[-1]["failure_kind"] == "passed",
            "rounds_used": len(history) - 1, "usage": usage_total, "history": history,
            "solution": code, "model": args.model or os.environ.get("LLM_MODEL"),
            "temperature_used": sorted(temps_used)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", choices=["humaneval", "classeval", "original"], default="humaneval",
                    help="original = data/original30 新写的 30 道题")
    ap.add_argument("--model", default=None, help="模型名（默认读取 LLM_MODEL）")
    ap.add_argument("--prompt", choices=["direct", "syntax"], default="syntax")
    ap.add_argument("--feedback", choices=["blind", "raw", "hint", "rag"], default="raw")
    ap.add_argument("--rounds", type=int, default=3, help="最多修复轮数（0 = 不修复，即单次生成基线）")
    ap.add_argument("--init", help="已有的第 0 轮 solutions jsonl（如 CangjieBench 公开结果）")
    ap.add_argument("--strip-main", action="store_true", help="自动删除模型生成的 main()")
    ap.add_argument("--compile-only-feedback", action="store_true",
                    help="零测试泄漏模式：修复阶段仅编译 solution，不接触任何 test 代码")
    ap.add_argument("--all-tests", action="store_true",
                    help="仅 ClassEval：每轮运行全部测试（方法级 + 集成），全部通过才停止，反馈合并所有失败测试")
    ap.add_argument("--temperature", type=float, default=0.0, help="采样温度（重复实验时可设为 0.3）")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ids", help="只跑指定题号，逗号分隔")
    ap.add_argument("-j", "--workers", type=int, default=4)
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    if args.all_tests and args.dataset != "classeval":
        ap.error("--all-tests 只适用于 --dataset classeval")
    ds = {"humaneval": load_humaneval, "classeval": load_classeval, "original": load_original30}[args.dataset]()
    if args.all_tests:
        tests = load_classeval_tests()
        ds = {k: dict(v, tests=tests[str(k)]["tests"]) for k, v in ds.items()}
    syntax_rule = load_syntax_rule() if args.prompt == "syntax" else ""
    init = {str(r["id"]): r["solution"] for r in read_jsonl(args.init)} if args.init else {}
    items = list(ds.values())
    if args.ids:
        keep = {str(x) for x in args.ids.split(",")}
        items = [it for it in items if str(it["id"]) in keep]
    if args.limit:
        items = items[: args.limit]

    # 断点续跑：读取已完成且无 error 的题目，边跑边追加写入
    done: dict[str, dict] = {}
    if os.path.exists(args.output):
        for r in read_jsonl(args.output):
            if "error" not in r:
                done[str(r["id"])] = r
        print(f"[resume] 已完成 {len(done)}/{len(items)} 题，跳过")

    todo = [it for it in items if str(it["id"]) not in done]
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    lock = threading.Lock()

    def run(it):
        try:
            return solve(it, args, syntax_rule, init.get(str(it["id"])) if args.init else None)
        except Exception as e:
            return {"id": it["id"], "passed": False, "error": repr(e), "history": []}

    with open(args.output, "a", encoding="utf-8") as fout, ThreadPoolExecutor(args.workers) as ex:
        futs = [ex.submit(run, it) for it in todo]
        for fut in tqdm(as_completed(futs), total=len(futs)):
            row = fut.result()
            with lock:
                fout.write(json.dumps(row, ensure_ascii=False) + "\n")
                fout.flush()
            if "error" not in row:
                done[str(row["id"])] = row
            else:
                done.setdefault(str(row["id"]), row)

    rows = [done[str(it["id"])] for it in items if str(it["id"]) in done]
    rows.sort(key=lambda r: (0, int(r["id"])) if str(r["id"]).isdigit() else (1, str(r["id"])))
    write_jsonl(args.output, rows)

    # 汇总：每一轮累计通过率（画"通过率-轮数"曲线用）+ token 成本
    n = len(rows)
    curve = []
    for k in range(args.rounds + 1):
        ok = sum(1 for r in rows if r.get("passed") and r.get("rounds_used", 99) <= k)
        curve.append(round(100 * ok / n, 2))
    summary = {
        "config": vars(args), "n": n, "prompt_version": P.PROMPT_VERSION,
        "model_resolved": args.model or os.environ.get("LLM_MODEL"),
        "temperature_used": sorted({t for r in rows for t in r.get("temperature_used", [])}),
        "pass@1_by_round": curve,
        "round0_compile_rate": round(100 * sum(
            1 for r in rows if r.get("history") and r["history"][0]["failure_kind"] != "compile_error") / n, 2),
        "total_prompt_tokens": sum(r.get("usage", {}).get("prompt_tokens", 0) for r in rows),
        "total_completion_tokens": sum(r.get("usage", {}).get("completion_tokens", 0) for r in rows),
        "errors": sum(1 for r in rows if "error" in r),
    }
    with open(args.output.replace(".jsonl", "") + ".summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
