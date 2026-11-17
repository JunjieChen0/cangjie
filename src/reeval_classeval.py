"""ClassEval 全部测试复评（对齐 CangjieBench 官方 pass_rate 口径）。

官方 Pass@1 = 一道题的全部测试（test 列表）都通过；我们的修复实验只用了集成测试 test[-1]。
修复循环在 test[-1] 通过时停止，所以只有「最终通过 test[-1]」的代码需要补跑其余测试：
  第 k 轮全部测试通过  <=>  最终代码通过全部测试 且 rounds_used <= k

用法：
  # V1：官方参考答案
  python src/reeval_classeval.py --reference
  # V2：复评官方公开结果并与官方 records 逐测试比对
  python src/reeval_classeval.py --solutions <x_ClassEval.jsonl> --compare <x_ClassEval.jsonl.records.jsonl>
  # 正式复评我们的 ClassEval 实验（同时完成 V3：test[-1] 重跑一致性）
  python src/reeval_classeval.py
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import mcnemar_p  # noqa: E402
from data import CLASSEVAL, ROOT, read_jsonl, write_jsonl  # noqa: E402
from runner import compile_and_run  # noqa: E402

MAX_ROUND = 5


def load_classeval_tests() -> dict[str, dict]:
    """{id: {"solution": 参考答案, "tests": 完整测试列表}}（data.load_classeval 只给 test[-1]）。"""
    out = {}
    for d in read_jsonl(CLASSEVAL):
        tests = d["test"] if isinstance(d["test"], list) else [d["test"]]
        out[str(d["id"])] = {"solution": d["solution"], "tests": tests}
    return out


def round_curves(rows: list[dict], max_round: int = MAX_ROUND) -> tuple[list[float], list[float]]:
    """由每题的 rounds_used / passed_main / passed_all 算出两种口径的逐轮累计通过率（%）。"""
    n = len(rows)

    def curve(key: str) -> list[float]:
        return [round(100 * sum(1 for r in rows if r[key] and r["rounds_used"] <= k) / n, 2)
                for k in range(max_round + 1)]

    return curve("passed_main"), curve("passed_all")


def run_all_tests(jobs: list[tuple[str, str]], ds: dict[str, dict], workers: int) -> dict[str, list]:
    """jobs = [(id, solution)]，对每题的每个测试编译运行，返回 {id: [RunResult, ...]}（按测试顺序）。"""
    tasks = [(qid, i, sol, t) for qid, sol in jobs for i, t in enumerate(ds[qid]["tests"])]
    with ThreadPoolExecutor(workers) as ex:
        results = list(ex.map(lambda x: compile_and_run(x[2] + "\n" + x[3]), tasks))
    out: dict[str, list] = defaultdict(list)
    for (qid, _, _, _), res in sorted(zip(tasks, results), key=lambda p: (p[0][0], p[0][1])):
        out[qid].append(res)
    return out


def compare_with_official(status: dict[str, list[bool]], records_path: str) -> None:
    official = {str(r["id"]): r["run_result"]["status"] for r in read_jsonl(records_path)}
    same = total = 0
    diffs = []
    for q, s in status.items():
        o = official.get(q)
        if o is None or len(o) != len(s):
            diffs.append((q, "len", s, o))
            continue
        for i, (a, b) in enumerate(zip(s, o)):
            total += 1
            same += a == b
            if a != b:
                diffs.append((q, i, a, b))
    print(f"与官方 records 逐测试一致：{same}/{total} ({100 * same / max(total, 1):.2f}%)")
    for d in diffs[:20]:
        print(f"  不一致 id={d[0]} test={d[1]} ours={d[2]} official={d[3]}")


def check_solutions(jobs, ds, workers, compare: str | None) -> None:
    """V1 / V2：对给定 solutions 跑全部测试，打印两种口径，可选与官方 records 逐测试比对。"""
    res = run_all_tests(jobs, ds, workers)
    status = {q: [r.passed for r in rs] for q, rs in res.items()}
    n = len(status)
    n_all = sum(all(s) for s in status.values())
    n_main = sum(s[-1] for s in status.values())
    print(f"N={n}  全部测试通过={n_all} ({100 * n_all / n:.1f}%)  test[-1]通过={n_main} ({100 * n_main / n:.1f}%)")
    if compare:
        compare_with_official(status, compare)
        return
    for q, s in sorted(status.items(), key=lambda p: int(p[0])):
        if not all(s):
            print(f"  未全部通过 id={q}: {[r.failure_kind for r in res[q]]}")


def reeval_experiment(path: str, ds: dict[str, dict], workers: int, out_dir: str) -> list[dict]:
    rows = read_jsonl(path)
    jobs = [(str(r["id"]), r["solution"]) for r in rows if r.get("passed")]
    res = run_all_tests(jobs, ds, workers)
    out = []
    for r in rows:
        qid = str(r["id"])
        if qid in res:
            st = [x.passed for x in res[qid]]
            rec = {"id": qid, "rounds_used": r["rounds_used"], "passed_main": True,
                   "passed_all": all(st), "status": st,
                   "failure_kinds": [x.failure_kind for x in res[qid]],
                   "main_rerun_passed": st[-1]}
        else:
            rec = {"id": qid, "rounds_used": r.get("rounds_used", MAX_ROUND), "passed_main": False,
                   "passed_all": False, "status": None, "failure_kinds": None,
                   "main_rerun_passed": None, "note": "not_reevaluated"}
        out.append(rec)
    name = os.path.basename(path).replace(".jsonl", "")
    write_jsonl(os.path.join(out_dir, f"{name}.alltests.jsonl"), out)
    main, all_ = round_curves(out)
    unstable = [r["id"] for r in out if r["passed_main"] and not r["main_rerun_passed"]]
    summary = {"name": name, "n": len(out), "curve_main": main, "curve_all": all_,
               "final_main": sum(r["passed_main"] for r in out),
               "final_all": sum(r["passed_all"] for r in out),
               "main_rerun_unstable_ids": unstable}
    with open(os.path.join(out_dir, f"{name}.alltests.summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return out


def print_report(results: dict[str, list[dict]]) -> None:
    print(f"\n{'实验':32s} | 口径 | " + " ".join(f"{'R' + str(k):>6s}" for k in range(MAX_ROUND + 1)) + " | V3不稳定")
    print("-" * 100)
    for name, rows in results.items():
        main, all_ = round_curves(rows)
        unstable = sum(1 for r in rows if r["passed_main"] and not r["main_rerun_passed"])
        print(f"{name:32s} | main | " + " ".join(f"{v:5.2f}%" for v in main) + f" | {unstable}")
        print(f"{'':32s} | all  | " + " ".join(f"{v:5.2f}%" for v in all_))

    print("\n=== 全部测试口径下的 McNemar 检验 ===")
    groups: dict[str, dict] = defaultdict(dict)
    for name, rows in results.items():
        m = re.match(r"^(.+)_(blind|raw|hint)_r\d+$", name)
        if m:
            groups[m.group(1)][m.group(2)] = [
                {"id": r["id"], "passed": r["passed_all"], "rounds_used": r["rounds_used"]} for r in rows]
    for prefix, grp in sorted(groups.items()):
        for a, b in [("hint", "raw"), ("hint", "blind"), ("raw", "blind")]:
            if a in grp and b in grp:
                for k in (1, 2, 3, 5):
                    ca, cb, pv = mcnemar_p(grp[a], grp[b], k)
                    sig = "*" if pv < 0.05 else ""
                    print(f"  {prefix} | R{k} {a} vs {b}: {a}_only={ca}, {b}_only={cb}, p={pv:.4f} {sig}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", action="store_true", help="V1：复评官方参考答案")
    ap.add_argument("--solutions", help="V2：复评一个官方 solutions jsonl（所有题、所有测试）")
    ap.add_argument("--compare", help="V2：与之逐测试比对的官方 records jsonl")
    ap.add_argument("--exp-glob", default=os.path.join(ROOT, "results", "exp", "*_ce_*_r5.jsonl"))
    ap.add_argument("--out-dir", default=os.path.join(ROOT, "results", "reeval"))
    ap.add_argument("-j", "--workers", type=int, default=2)
    a = ap.parse_args()

    ds = load_classeval_tests()
    if a.reference:
        check_solutions([(q, d["solution"]) for q, d in ds.items()], ds, a.workers, None)
        return
    if a.solutions:
        jobs = [(str(r["id"]), r["solution"]) for r in read_jsonl(a.solutions)]
        check_solutions(jobs, ds, a.workers, a.compare)
        return

    os.makedirs(a.out_dir, exist_ok=True)
    paths = sorted(p for p in glob.glob(a.exp_glob) if not p.endswith(".records.jsonl"))
    results = {}
    for p in paths:
        name = os.path.basename(p).replace(".jsonl", "")
        print(f"[reeval] {name}")
        results[name] = reeval_experiment(p, ds, a.workers, a.out_dir)
    print_report(results)


if __name__ == "__main__":
    main()
