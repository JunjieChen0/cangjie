"""ClassEval 修复 5 轮后仍失败的题（剩余失败）分析，以及反馈截断检查（只读结果文件，不调用模型 API）。

- 剩余失败：每个配置（模型 × 起点 × 反馈）5 轮后仍失败的题次，按最后一轮失败类别统计（API 超时单列）；
  测试失败中“只差一个测试”（n 个测试过了 n−1 个）的比例；每次重复都失败的题。
- 固定难题清单：某模型在 raw / hint / rag 三种反馈的每次重复中都失败的题，附最后一轮失败类别、测试通过情况与反馈开头，
  “人工归类”一列取自手工维护的 results/stats/hard_problem_coding.csv。
- 截断检查：给模型看过的反馈（每题最后一轮之前的各轮）在日志里只存了前 STORED_CAP 个字符。存下的不足 STORED_CAP 的，
  原文也不足，肯定没有被 repair.FEEDBACK_CAP（3000）截断；存满的不确定。--recheck 会在本地重新编译运行这些轮的代码，
  算出未截断的反馈长度（只调用 cjc，不调用模型 API）。

用法：
  python src/residual_failures.py                      # → results/stats/residual_failures.{md,json}
  python src/residual_failures.py --recheck -j 6       # 另外复查存满的反馈（需要 cjc，较慢）
"""
from __future__ import annotations

import argparse
import ast
import csv
import glob
import json
import os
import re
import statistics as st
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import classify_error  # noqa: E402
from data import ROOT  # noqa: E402
from stage3_stats import parse_name  # noqa: E402

STORED_CAP = 1500          # repair.py 写 history 时 feedback 只存前 1500 个字符
FEEDBACK_CAP = 3000        # repair.FEEDBACK_CAP：给模型看的反馈总长上限
BASE = os.path.join(ROOT, "results", "stage3")
OUT = os.path.join(ROOT, "results", "stats")
CODING = os.path.join(OUT, "hard_problem_coding.csv")   # 固定难题的人工归类（初稿 + 复核），手工维护，脚本只读
ARMS = ("raw", "hint", "rag")


def last_failure(row: dict) -> str:
    """一道题最终未通过的原因：API 超时，或最后一轮评测的错误类别（analyze.classify_error）。"""
    if "error" in row:
        return "api_timeout"
    return classify_error(row["history"][-1])


def is_near_miss(status) -> bool:
    """status 为各测试是否通过的列表（日志中为 JSON 列表，也接受 "[True, False]" 形式的字符串）：恰好一个测试没过。"""
    if isinstance(status, str):
        try:
            status = ast.literal_eval(status) if status else []
        except (ValueError, SyntaxError):
            return False
    return bool(status) and sum(not x for x in status) == 1


_LOCAL_PATH = re.compile(r"\((?:[A-Za-z]:)?[\\/][^()]*\)")


def clean_feedback(text: str, limit: int = 160) -> str:
    """压成一行、去掉形如 (C:\\Users\\...\\main.cj:3) 的本机路径，截到 limit 个字符。"""
    return " ".join(_LOCAL_PATH.sub("", text).split())[:limit]


def residual_summary(reps: list[dict[str, dict]]) -> dict:
    """reps：每次重复 {题号: 记录}。返回失败题次、类别分布、测试失败数、只差一个测试数、每次都失败的题号。"""
    cats, test_fail, near, fail_count = Counter(), 0, 0, Counter()
    for rows in reps:
        for i, r in rows.items():
            if r.get("passed"):
                continue
            c = last_failure(r)
            cats[c] += 1
            fail_count[i] += 1
            if c == "test_failure":
                test_fail += 1
                near += is_near_miss(r["history"][-1].get("status", ""))
    return {"fail": sum(cats.values()), "cats": dict(cats), "test_fail": test_fail, "near_miss": near,
            "always": sorted((i for i, n in fail_count.items() if n == len(reps)), key=int)}


def truncation_census(rows) -> Counter:
    """给模型看过的反馈（每题最后一条之前）按 (失败类别, 是否存满 STORED_CAP) 计数。"""
    c = Counter()
    for r in rows:
        for e in (r.get("history") or [])[:-1]:
            c[(e["failure_kind"], len(e.get("feedback", "")) >= STORED_CAP)] += 1
    return c


def _full_msg(r) -> str:
    """runner.RunResult.feedback 去掉 3000 字符截断后的文本。"""
    if r.failure_kind == "compile_error":
        return r.compile_stderr
    if r.failure_kind == "timeout":
        return "Execution timed out (possible infinite loop)."
    return (r.run_stderr + "\n" + r.run_stdout).strip()


def full_feedback_text(results: list) -> str:
    """与 repair.aggregate_feedback 相同的拼接方式，但不截断。"""
    if all(r.passed for r in results):
        return ""
    compile_errs = [(i, _full_msg(r)) for i, r in enumerate(results) if r.failure_kind == "compile_error"]
    if compile_errs:
        seen, parts = set(), []
        for i, m in compile_errs:
            if m not in seen:
                seen.add(m)
                parts.append((i, m))
        if len(parts) == 1:
            return parts[0][1]
        return "\n\n".join(f"[with test #{i}]\n{m}" for i, m in parts)
    failed = [(i, r) for i, r in enumerate(results) if not r.passed]
    text = "\n\n".join(f"[test #{i} {r.failure_kind}]\n{_full_msg(r)}" for i, r in failed)
    return f"{len(failed)} of {len(results)} tests failed.\n\n" + text


def full_feedback_length(results: list) -> int:
    return len(full_feedback_text(results))


def error_line_retention(text: str, cap: int = FEEDBACK_CAP) -> tuple[int, int]:
    """(全文中以 "error:" 开头的行数, 截到前 cap 个字符后仍完整以 "error:" 开头的行数)。"""
    def count(t: str) -> int:
        return sum(line.lstrip().startswith("error:") for line in t.splitlines())
    return count(text), count(text[:cap])


def load_runs(base: str, ds: str) -> dict[tuple, list[dict[str, dict]]]:
    """{(模型, 起点, 反馈): [每次重复 {题号: 记录}]}；同一题有多行时无错误的行优先（同 stage3_stats.load_groups）。"""
    out: dict[tuple, dict[int, dict]] = defaultdict(dict)
    for p in sorted(glob.glob(os.path.join(base, "runs", f"*_{ds}_*_rep*.jsonl"))):
        parsed = parse_name(os.path.basename(p)[: -len(".jsonl")])
        if parsed is None or parsed[1] != ds:
            continue
        model, _, prompt, fb, rep = parsed
        rows: dict[str, dict] = {}
        with open(p, encoding="utf-8") as f:
            for r in (json.loads(line) for line in f if line.strip()):
                if "error" not in r or str(r["id"]) not in rows:
                    rows[str(r["id"])] = r
        out[(model, prompt, fb)][rep] = rows
    return {k: [v[r] for r in sorted(v)] for k, v in out.items()}


def hard_problems(runs: dict[tuple, list], model: str, prompt: str = "direct") -> list[dict]:
    """在 raw / hint / rag 三种反馈的每次重复中都失败的题，附第一条非超时记录（按 raw、hint、rag 与重复的顺序）最后一轮的信息。"""
    arms = [runs[(model, prompt, fb)] for fb in ARMS if (model, prompt, fb) in runs]
    if not arms:
        return []
    always = set.intersection(*(set(residual_summary(reps)["always"]) for reps in arms))
    out = []
    for i in sorted(always, key=int):
        records = [rows[i] for reps in arms for rows in reps]
        last = next((r["history"][-1] for r in records if "error" not in r and r.get("history")), {})
        m = re.search(r"\bclass\s+(\w+)", last.get("code", ""))
        out.append({"id": i, "class": m.group(1) if m else "", "kinds": sorted({last_failure(r) for r in records}),
                    "status": last.get("status", ""), "feedback_head": clean_feedback(last.get("feedback", ""))})
    return out


def summarize_recheck(items: list[tuple[str, int, str]]) -> dict:
    """items：(“模型 失败类别”, 出现次数, 未截断全文)。按出现次数加权统计：复查次数、去重后的代码数、超过 FEEDBACK_CAP 的次数，
    超长反馈中 "error:" 行的总数与截断后保留数、报错行全部丢失的次数，以及全文长度的中位数 / 90 分位 / 最大值。"""
    out: dict = {}
    for key in sorted({k for k, _, _ in items}):
        sub = [(w, t) for k, w, t in items if k == key]
        lengths = sorted(len(t) for w, t in sub for _ in range(w))
        d = {"checked": len(lengths), "unique_code": len(sub), "over_cap": 0,
             "error_lines_total": 0, "error_lines_kept": 0, "lost_all_errors": 0,
             "length_median": st.median(lengths), "length_p90": lengths[int(0.9 * (len(lengths) - 1))],
             "length_max": lengths[-1]}
        for w, t in sub:
            if len(t) <= FEEDBACK_CAP:
                continue
            total, kept = error_line_retention(t)
            d["over_cap"] += w
            d["error_lines_total"] += w * total
            d["error_lines_kept"] += w * kept
            d["lost_all_errors"] += w * (total > 0 and kept == 0)
        out[key] = d
    return out


def recheck(runs: dict[tuple, list], models: tuple[str, ...], workers: int) -> dict:
    """重新编译运行存满 STORED_CAP 的那些轮的代码（同一题同一份代码只跑一次），得到未截断的反馈全文（需要 cjc）。"""
    from reeval_classeval import load_classeval_tests
    from runner import compile_and_run
    tests = load_classeval_tests()
    jobs: Counter = Counter()
    for (model, _, fb), reps in runs.items():
        if model not in models or fb == "blind":
            continue
        for rows in reps:
            for i, r in rows.items():
                for e in (r.get("history") or [])[:-1]:
                    if len(e.get("feedback", "")) >= STORED_CAP:
                        jobs[(f"{model} {e['failure_kind']}", i, e["code"])] += 1

    def run(job):
        key, i, code = job
        return key, jobs[job], full_feedback_text([compile_and_run(code + "\n" + t) for t in tests[i]["tests"]])

    with ThreadPoolExecutor(max_workers=workers) as ex:
        return summarize_recheck(list(ex.map(run, list(jobs))))


def load_coding(path: str = CODING) -> dict[str, dict]:
    """人工归类表 {题号: 行}（列：id, class, category, subtype, evidence, coder, reviewer）；文件不存在时为空。"""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        return {row["id"]: row for row in csv.DictReader(f)}


def coding_label(row: dict, coding: dict[str, dict]) -> str:
    """固定难题的归类：该模型每次都是 API 超时的题没有代码可分析，单独标出；其余取归类表的“主类：子类”。"""
    if row["kinds"] == ["api_timeout"]:
        return "API 超时（无代码）"
    c = coding.get(row["id"])
    return f"{c['category']}：{c['subtype']}" if c else ""


def write_markdown(table: list[dict], census: dict, hard: dict, rechecked: dict | None,
                   coding: dict[str, dict] | None = None) -> str:
    coding = coding or {}
    L = ["# ClassEval 剩余失败与反馈截断检查（自动生成）", "",
         "数据：`results/stage3/runs/` 中 ClassEval 各组（全部测试驱动修复）。题次 = 题 × 重复。", "",
         "## 修复 5 轮后仍失败的题次", "",
         "| 模型 | 起点 | 反馈 | 重复 | 失败题次 | 测试失败 | 其中只差一个测试 | API 超时 | 编译/其他 | 每次都失败的题数 |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for t in table:
        c = t["cats"]
        other = t["fail"] - c.get("test_failure", 0) - c.get("api_timeout", 0)
        near = f"{t['near_miss']}（{100 * t['near_miss'] / t['test_fail']:.0f}%）" if t["test_fail"] else "0"
        L.append(f"| {t['model']} | {t['prompt']} | {t['feedback']} | {t['reps']} | {t['fail']} | "
                 f"{c.get('test_failure', 0)} | {near} | {c.get('api_timeout', 0)} | {other} | {len(t['always'])} |")
    L += ["", "编译/其他 包括 api_or_undeclared、foreign_syntax、type_or_mutability、runtime_exception 等，"
          "完整分布见 json 中的 cats。", "",
          "## 固定难题：raw / hint / rag 每次重复都失败的题（`direct` 起点）", "",
          f"“人工归类”取自 `{os.path.relpath(CODING, ROOT)}`（逐题依据见该文件 evidence 列；coder / reviewer 列记录编码人与复核人）。"
          "修复反馈只给出失败的测试函数名，不给断言内容与期望值。", ""]
    for model, rows in hard.items():
        counts = Counter(coding_label(r, coding) or "未归类" for r in rows)
        L += [f"### {model}（{len(rows)} 题）", "",
              "归类计数：" + "；".join(f"{k} {v}" for k, v in counts.most_common()), "",
              "| 题号 | 类名 | 最终失败类别 | 测试通过情况（第一条非超时记录） | 反馈开头 | 人工归类 |", "|---|---|---|---|---|---|"]
        for r in rows:
            fb = r["feedback_head"].replace("|", "\\|")
            st = "".join("✓" if x else "✗" for x in r["status"]) if isinstance(r["status"], list) else r["status"]
            L.append(f"| {r['id']} | {r['class']} | {', '.join(r['kinds'])} | {st} | {fb} | {coding_label(r, coding)} |")
        L.append("")
    L += ["## 反馈截断检查", "",
          f"给模型看过的反馈（每题最后一轮之前）按日志中是否存满 {STORED_CAP} 字符计数。未存满的，原文也不足 {STORED_CAP} 字符，"
          f"肯定没有被 {FEEDBACK_CAP} 字符截断；存满的需要重新运行才能确定。", "",
          "| 模型 | 失败类别 | 未存满（未截断） | 存满（待确定） |", "|---|---|---|---|"]
    for key in sorted(census):
        model, kind = key.split(" ", 1)
        L.append(f"| {model} | {kind} | {census[key].get('short', 0)} | {census[key].get('at_cap', 0)} |")
    if rechecked is not None:
        L += ["", f"### 重新运行存满的反馈（未截断长度是否超过 {FEEDBACK_CAP} 字符）", "",
              "同一题同一份代码只重新运行一次，再按出现次数加权。报错行 = 以 `error:` 开头的行；"
              f"“保留”指截到前 {FEEDBACK_CAP} 个字符后该行开头仍在。长度为存满的那些反馈的未截断全文长度（字符）。", "",
              "| 模型 与 失败类别 | 复查条数（去重后代码） | 超过上限（被截断） | 被截断者的报错行保留 | 报错行全部丢失 | 长度中位数 / 90 分位 / 最大 |",
              "|---|---|---|---|---|---|"]
        for k, v in sorted(rechecked.items()):
            kept = (f"{v['error_lines_kept']} / {v['error_lines_total']}"
                    f"（{100 * v['error_lines_kept'] / v['error_lines_total']:.1f}%）") if v["error_lines_total"] else "—"
            L.append(f"| {k} | {v['checked']}（{v['unique_code']}） | {v['over_cap']} | {kept} | {v['lost_all_errors']} | "
                     f"{v['length_median']:g} / {v['length_p90']} / {v['length_max']} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--models", default="ds_v41f,kimik31p", help="剩余失败分析的模型（逗号分隔）")
    ap.add_argument("--recheck", action="store_true", help="重新运行存满的反馈（需要 cjc）")
    ap.add_argument("--recheck-models", default="ds_v41f,kimik31p,doubao_mini")
    ap.add_argument("-j", type=int, default=4)
    args = ap.parse_args()
    runs = load_runs(args.base, "ce")
    models = tuple(args.models.split(","))
    table = [{"model": m, "prompt": p, "feedback": fb, "reps": len(reps), **residual_summary(reps)}
             for (m, p, fb), reps in sorted(runs.items()) if m in models and not fb.endswith("_co")]
    census: dict[str, dict] = defaultdict(lambda: {"short": 0, "at_cap": 0})
    for (m, _, fb), reps in runs.items():
        if fb == "blind":
            continue
        for rows in reps:
            for (kind, at_cap), n in truncation_census(rows.values()).items():
                census[f"{m} {kind}"]["at_cap" if at_cap else "short"] += n
    hard = {m: hard_problems(runs, m) for m in models}
    rechecked = recheck(runs, tuple(args.recheck_models.split(",")), args.j) if args.recheck else None
    os.makedirs(args.out, exist_ok=True)
    stem = os.path.join(args.out, "residual_failures")
    with open(stem + ".json", "w", encoding="utf-8") as f:
        json.dump({"residual": table, "truncation_census": census, "hard_problems": hard, "recheck": rechecked},
                  f, ensure_ascii=False, indent=1)
    with open(stem + ".md", "w", encoding="utf-8") as f:
        f.write(write_markdown(table, census, hard, rechecked, load_coding()))
    print(f"→ {stem}.md")


if __name__ == "__main__":
    main()
