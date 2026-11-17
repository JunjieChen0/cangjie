"""第 3 阶段实验矩阵的批量运行器（调用 src/repair.py）。

协议：T=0.3（Kimi 只允许 T=1）、每组 3 次重复、共享第 0 轮、提示 v2、最多 5 轮修复、ClassEval 全部测试驱动。
先生成全部第 0 轮（阶段 1），再跑各修复组（阶段 2）；已完成的组自动跳过，中断后重跑同一命令即可续跑。

用法：
  python src/run_matrix.py --dry-run                 # 只打印命令
  python src/run_matrix.py --pilot -p 2              # 试跑：每组 10 题，输出到 results/stage3/pilot/
  python src/run_matrix.py -p 2 --only doubao        # 正式跑（--only 按名称正则筛选）
  python src/run_matrix.py --check                   # 只做检查：完成度、errors、第 0 轮一致性、实际温度
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import ROOT  # noqa: E402

MODELS = {
    "ds_v41f": "deepseek-v4-1-flash-261017",
    "doubao_mini": "doubao-seed-2-0-mini-260428",
    "kimik31p": "kimi-k3-1-pro-261024",
}
N_TASKS = {"he": 164, "ce": 84}
PILOT_LIMIT = 10
TEMP = 0.3
KIMI_TEMP = 1.0
REPS = (1, 2, 3)
ROUNDS = 5


@dataclass
class Job:
    name: str
    model: str
    ds: str                      # he / ce
    prompt: str                  # direct / syntax
    temp: float
    feedback: str | None = None  # None 表示第 0 轮
    compile_only: bool = False
    rep: int = 0
    env: dict = field(default_factory=dict)

    @property
    def r0_name(self) -> str:
        return f"{self.model}_{self.ds}_{self.prompt}_r0"


def _repairs(model, ds, prompt, feedbacks, reps=REPS, temp=TEMP, compile_only=False, env=None):
    tag = "_co" if compile_only else ""
    return [Job(f"{model}_{ds}_{prompt}_{fb}{tag}_rep{r}", model, ds, prompt, temp, fb, compile_only, r, env or {})
            for fb in feedbacks for r in reps]


def expand_matrix() -> tuple[list[Job], list[Job]]:
    """返回 (第 0 轮任务, 修复任务)。"""
    four = ("blind", "raw", "hint", "rag")
    rep = []
    for m in ("ds_v41f", "doubao_mini"):                               # A：HumanEval 主矩阵
        for p in ("direct", "syntax"):
            rep += _repairs(m, "he", p, four)
    for m in ("ds_v41f", "doubao_mini"):                               # B：ClassEval 全部测试驱动
        rep += _repairs(m, "ce", "direct", four)
    rep += _repairs("doubao_mini", "ce", "syntax", ("raw", "hint", "rag"))
    for m in ("ds_v41f", "doubao_mini"):                               # C：只给编译错误
        rep += _repairs(m, "he", "direct", ("raw", "hint", "rag"), compile_only=True)
    rep += _repairs("kimik31p", "he", "direct", ("raw", "hint"), temp=KIMI_TEMP)            # D：Kimi
    rep += _repairs("kimik31p", "ce", "direct", ("raw", "hint"), reps=(1,), temp=KIMI_TEMP,
                    env={"LLM_TIMEOUT": "600"})
    r0, seen = [], set()
    for j in rep:
        if j.r0_name not in seen:
            seen.add(j.r0_name)
            r0.append(Job(j.r0_name, j.model, j.ds, j.prompt, j.temp, env=j.env))
    return r0, rep


def out_dir(pilot: bool) -> str:
    return os.path.join(ROOT, "results", "stage3", "pilot" if pilot else "")


def output_path(job: Job, base: str) -> str:
    sub = "r0" if job.feedback is None else "runs"
    return os.path.join(base, sub, f"{job.name}.jsonl")


def build_cmd(job: Job, base: str, pilot: bool, workers: int) -> list[str]:
    cmd = [sys.executable, os.path.join(ROOT, "src", "repair.py"),
           "--dataset", "humaneval" if job.ds == "he" else "classeval",
           "--model", MODELS[job.model], "--prompt", job.prompt, "--strip-main",
           "--temperature", str(job.temp), "-j", str(workers), "-o", output_path(job, base)]
    if job.ds == "ce":
        cmd.append("--all-tests")
    if job.feedback is None:
        cmd += ["--rounds", "0"]
    else:
        r0 = Job(job.r0_name, job.model, job.ds, job.prompt, job.temp)
        cmd += ["--rounds", str(ROUNDS), "--feedback", job.feedback, "--init", output_path(r0, base)]
        if job.compile_only:
            cmd.append("--compile-only-feedback")
    if pilot:
        cmd += ["--limit", str(PILOT_LIMIT)]
    return cmd


def read_summary(job: Job, base: str) -> dict | None:
    p = output_path(job, base).replace(".jsonl", "") + ".summary.json"
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def is_done(job: Job, base: str, pilot: bool) -> bool:
    s = read_summary(job, base)
    expected = PILOT_LIMIT if pilot else N_TASKS[job.ds]
    return bool(s) and s.get("n") == expected and s.get("errors") == 0


def run_job(job: Job, base: str, pilot: bool, workers: int) -> tuple[str, int]:
    log_dir = os.path.join(base, "logs")
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_path(job, base)), exist_ok=True)
    env = dict(os.environ, PYTHONIOENCODING="utf-8", **job.env)
    with open(os.path.join(log_dir, f"{job.name}.log"), "a", encoding="utf-8") as log:
        code = subprocess.call(build_cmd(job, base, pilot, workers), stdout=log, stderr=subprocess.STDOUT,
                               cwd=ROOT, env=env)
    return job.name, code


def run_phase(jobs: list[Job], base: str, pilot: bool, parallel: int, workers: int) -> list[str]:
    todo = [j for j in jobs if not is_done(j, base, pilot)]
    print(f"  待运行 {len(todo)} / {len(jobs)}（其余已完成，跳过）")
    by_name = {j.name: j for j in todo}
    failed = []
    with ThreadPoolExecutor(parallel) as ex:
        for name, code in ex.map(lambda j: run_job(j, base, pilot, workers), todo):
            ok = code == 0 and is_done(by_name[name], base, pilot)
            print(f"  [{'完成' if ok else '未完成'}] {name}" + ("" if ok else f"（退出码 {code}，见 logs/{name}.log）"))
            if not ok:
                failed.append(name)
    return failed


def first_round_kinds(path: str) -> dict[str, str]:
    with open(path, encoding="utf-8") as f:
        return {str(r["id"]): r["history"][0]["failure_kind"] for r in map(json.loads, f) if r.get("history")}


def r0_mismatches(job: Job, base: str) -> int:
    """修复组第 0 轮的判定应与共享的第 0 轮文件逐题一致；返回不一致题数。"""
    if job.compile_only:  # 只给编译错误时第 0 轮判定的是“能否编译”，口径不同，不比较
        return 0
    r0 = first_round_kinds(output_path(Job(job.r0_name, job.model, job.ds, job.prompt, job.temp), base))
    mine = first_round_kinds(output_path(job, base))
    return sum(1 for i, k in mine.items() if r0.get(i) != k)


def check(r0_jobs: list[Job], rep_jobs: list[Job], base: str, pilot: bool) -> bool:
    ok = True
    for j in r0_jobs + rep_jobs:
        s = read_summary(j, base)
        if s is None:
            print(f"  [缺失] {j.name}")
            ok = False
            continue
        problems = []
        if not is_done(j, base, pilot):
            problems.append(f"n={s.get('n')} errors={s.get('errors')}")
        temps = s.get("temperature_used", [])
        if temps and temps != [j.temp]:   # 全部题第 0 轮即通过时修复组不调用模型，记录为空
            problems.append(f"实际温度 {temps} ≠ 设定 {j.temp}")
        if j.feedback is not None:
            mism = r0_mismatches(j, base)
            if mism:
                problems.append(f"第 0 轮与共享文件不一致 {mism} 题")
        curve = s.get("pass@1_by_round", [])
        tail = f"R0 {curve[0]:.2f}% → R{len(curve) - 1} {curve[-1]:.2f}%" if curve else ""
        print(f"  [{'问题' if problems else '正常'}] {j.name:42s} {tail}  {'；'.join(problems)}")
        ok = ok and not problems
    return ok


def select(r0_jobs: list[Job], rep_jobs: list[Job], pattern: str | None) -> tuple[list[Job], list[Job]]:
    if not pattern:
        return r0_jobs, rep_jobs
    rep_jobs = [j for j in rep_jobs if re.search(pattern, j.name)]
    needed = {j.r0_name for j in rep_jobs}
    return [j for j in r0_jobs if j.name in needed or re.search(pattern, j.name)], rep_jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true", help=f"每组只跑 {PILOT_LIMIT} 题，输出到 results/stage3/pilot/")
    ap.add_argument("--only", help="只运行名称匹配该正则的组（所需的第 0 轮自动包含）")
    ap.add_argument("-p", "--parallel", type=int, default=1, help="同时运行的组数")
    ap.add_argument("-j", "--workers", type=int, default=4, help="每组内部的并发题数（传给 repair.py）")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true", help="只检查，不运行")
    args = ap.parse_args()

    r0_jobs, rep_jobs = select(*expand_matrix(), args.only)
    base = out_dir(args.pilot)
    print(f"矩阵：第 0 轮 {len(r0_jobs)} 组，修复 {len(rep_jobs)} 组；输出目录 {base}")

    if args.dry_run:
        for j in r0_jobs + rep_jobs:
            env = " ".join(f"{k}={v}" for k, v in j.env.items())
            print((env + " " if env else "") + " ".join(build_cmd(j, base, args.pilot, args.workers)))
        return
    if args.check:
        sys.exit(0 if check(r0_jobs, rep_jobs, base, args.pilot) else 1)

    print("阶段 1：生成共享的第 0 轮")
    if run_phase(r0_jobs, base, args.pilot, args.parallel, args.workers):
        print("第 0 轮未全部完成，停止（修复组依赖第 0 轮）。重跑同一命令可续跑。")
        sys.exit(1)
    print("阶段 2：修复组")
    failed = run_phase(rep_jobs, base, args.pilot, args.parallel, args.workers)
    print("检查：")
    ok = check(r0_jobs, rep_jobs, base, args.pilot)
    sys.exit(0 if ok and not failed else 1)


if __name__ == "__main__":
    main()
