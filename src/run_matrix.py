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
    "glm53f": "glm-5-3-flash-260828",            # 以下三个为审稿意见后的补充实验（review 矩阵）
    "doubao21l": "doubao-seed-2-1-lite-260915",
    "u2f": "u2-flash",                           # 云知声，走 UNISOUND_* 接口（见 llm.PROVIDERS），限流 20 RPM
}
N_TASKS = {"he": 164, "ce": 84, "or": 30}
DATASET_ARG = {"he": "humaneval", "ce": "classeval", "or": "original"}
OUT_SUBDIR = {"stage3": "stage3", "original": "original30", "review": "review"}
NEW_MODELS = ("glm53f", "doubao21l", "u2f")
KIMI_REVIEW_TIMEOUT = "1800"
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
    rounds: int = ROUNDS               # 修复轮数；agent 组为步数上限（每步一次模型调用）
    init_matrix: str | None = None     # 第 0 轮取自哪个矩阵的结果目录（None = 本矩阵自己生成）

    @property
    def r0_name(self) -> str:
        return f"{self.model}_{self.ds}_{self.prompt}_r0"


AGENT_ARMS = {"agent": ROUNDS, "agent15": 15}       # Agent 基线：与修复循环同预算（5 步）与放宽预算（15 步）
FEEDBACK_ARG = {"agent15": "agent"}                 # 组名中的反馈 → repair.py --feedback 的取值


def _repairs(model, ds, prompt, feedbacks, reps=REPS, temp=TEMP, compile_only=False, env=None, init_matrix=None):
    tag = "_co" if compile_only else ""
    return [Job(f"{model}_{ds}_{prompt}_{fb}{tag}_rep{r}", model, ds, prompt, temp, fb, compile_only, r, env or {},
                AGENT_ARMS.get(fb, ROUNDS), init_matrix)
            for fb in feedbacks for r in reps]


FOUR = ("blind", "raw", "hint", "rag")


def _stage3_repairs() -> list[Job]:
    four = FOUR
    rep = []
    for m in ("ds_v41f", "doubao_mini"):                               # A：HumanEval 主矩阵
        for p in ("direct", "syntax"):
            rep += _repairs(m, "he", p, four)
    for m in ("ds_v41f", "doubao_mini"):                               # B：ClassEval 全部测试驱动
        rep += _repairs(m, "ce", "direct", four, env={"LLM_TIMEOUT": "600"} if m == "ds_v41f" else None)
    rep += _repairs("doubao_mini", "ce", "syntax", ("raw", "hint", "rag"))
    for m in ("ds_v41f", "doubao_mini"):                               # C：只给编译错误
        rep += _repairs(m, "he", "direct", ("raw", "hint", "rag"), compile_only=True)
    rep += _repairs("kimik31p", "he", "direct", ("raw", "hint"), temp=KIMI_TEMP)            # D：Kimi
    rep += _repairs("kimik31p", "ce", "direct", ("raw", "hint"), reps=(1,), temp=KIMI_TEMP,
                    env={"LLM_TIMEOUT": "600"})
    return rep


def _original_repairs() -> list[Job]:
    """新题集 Original-30：与第 3 阶段相同协议，用来检验结论在未见过的题目上是否成立。"""
    rep = []
    for m in ("ds_v41f", "doubao_mini"):                               # E1
        for p in ("direct", "syntax"):
            rep += _repairs(m, "or", p, FOUR)
    rep += _repairs("kimik31p", "or", "direct", ("raw", "hint"), temp=KIMI_TEMP)            # E2
    return rep


def _full(model: str, temp: float = TEMP, env: dict | None = None) -> list[Job]:
    """完整矩阵：HE / CE / Original-30 × direct / syntax × 四种反馈 × 3 次，另加 HE direct 只给编译错误的消融。"""
    rep = []
    for ds in ("he", "ce", "or"):
        for p in ("direct", "syntax"):
            rep += _repairs(model, ds, p, FOUR, temp=temp, env=env)
    return rep + _repairs(model, "he", "direct", ("raw", "hint", "rag"), temp=temp, compile_only=True, env=env)


def _review_repairs() -> list[Job]:
    """审稿意见后的补充实验（results/review/），协议同第 3 阶段，结果单独成族报告：
    三个新模型与 Kimi（超时放宽到 1800 秒、全新一套）各跑完整矩阵；补齐 DeepSeek ClassEval syntax。"""
    rep = []
    for m in NEW_MODELS:
        rep += _full(m, env={"LLM_TIMEOUT": "600"})
    rep += _full("kimik31p", temp=KIMI_TEMP, env={"LLM_TIMEOUT": KIMI_REVIEW_TIMEOUT})
    rep += _repairs("ds_v41f", "ce", "syntax", FOUR, env={"LLM_TIMEOUT": "600"})
    return rep + _arm_jobs(tuple(AGENT_ARMS)) + _arm_jobs(("rag2",))


def _arm_jobs(arms: tuple[str, ...]) -> list[Job]:
    """在全部 6 个模型上补跑新增的反馈组（agent / agent15 / rag2）。新模型与 Kimi 用 review 自己的第 0 轮；
    DeepSeek / Doubao 复用第 3 阶段与 Original-30 的共享第 0 轮，以便与原有修复组逐题配对。"""
    env, rep = {"LLM_TIMEOUT": "600"}, []
    for m in NEW_MODELS + ("kimik31p",):
        temp = KIMI_TEMP if m == "kimik31p" else TEMP
        menv = {"LLM_TIMEOUT": KIMI_REVIEW_TIMEOUT} if m == "kimik31p" else env
        for ds in ("he", "ce", "or"):
            for p in ("direct", "syntax"):
                rep += _repairs(m, ds, p, arms, temp=temp, env=menv)
    for m in ("ds_v41f", "doubao_mini"):
        for p in ("direct", "syntax"):
            rep += _repairs(m, "he", p, arms, env=env, init_matrix="stage3")
            rep += _repairs(m, "or", p, arms, env=env, init_matrix="original")
        rep += _repairs(m, "ce", "direct", arms, env=env, init_matrix="stage3")
    rep += _repairs("doubao_mini", "ce", "syntax", arms, env=env, init_matrix="stage3")
    return rep + _repairs("ds_v41f", "ce", "syntax", arms, env=env)        # 第 0 轮在 review 中新生成


def expand_matrix(matrix: str = "stage3") -> tuple[list[Job], list[Job]]:
    """返回 (第 0 轮任务, 修复任务)。matrix 为 stage3（默认）、original 或 review。
    第 0 轮取自其他矩阵的修复组（init_matrix）不在本矩阵生成第 0 轮。"""
    rep = {"stage3": _stage3_repairs, "original": _original_repairs, "review": _review_repairs}[matrix]()
    r0, seen = [], set()
    for j in rep:
        if j.init_matrix is None and j.r0_name not in seen:
            seen.add(j.r0_name)
            r0.append(Job(j.r0_name, j.model, j.ds, j.prompt, j.temp, env=j.env))
    return r0, rep


def out_dir(pilot: bool, matrix: str = "stage3") -> str:
    return os.path.join(ROOT, "results", OUT_SUBDIR[matrix], "pilot" if pilot else "")


def output_path(job: Job, base: str) -> str:
    sub = "r0" if job.feedback is None else "runs"
    return os.path.join(base, sub, f"{job.name}.jsonl")


def r0_path(job: Job, base: str, pilot: bool) -> str:
    """修复组所用第 0 轮文件：默认在本矩阵目录，init_matrix 指定时取那个矩阵的结果目录。"""
    r0 = Job(job.r0_name, job.model, job.ds, job.prompt, job.temp)
    return output_path(r0, out_dir(pilot, job.init_matrix) if job.init_matrix else base)


def build_cmd(job: Job, base: str, pilot: bool, workers: int) -> list[str]:
    cmd = [sys.executable, os.path.join(ROOT, "src", "repair.py"),
           "--dataset", DATASET_ARG[job.ds],
           "--model", MODELS[job.model], "--prompt", job.prompt, "--strip-main",
           "--temperature", str(job.temp), "-j", str(workers), "-o", output_path(job, base)]
    if job.ds == "ce":
        cmd.append("--all-tests")
    if job.feedback is None:
        cmd += ["--rounds", "0"]
    else:
        cmd += ["--rounds", str(job.rounds), "--feedback", FEEDBACK_ARG.get(job.feedback, job.feedback),
                "--init", r0_path(job, base, pilot)]
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


def r0_mismatches(job: Job, base: str, pilot: bool = False) -> int:
    """修复组第 0 轮的判定应与共享的第 0 轮文件逐题一致；返回不一致题数。"""
    if job.compile_only:  # 只给编译错误时第 0 轮判定的是“能否编译”，口径不同，不比较
        return 0
    r0 = first_round_kinds(r0_path(job, base, pilot))
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
            mism = r0_mismatches(j, base, pilot)
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
    ap.add_argument("--matrix", choices=sorted(OUT_SUBDIR), default="stage3",
                    help="stage3 = 第 3 阶段矩阵（results/stage3/）；original = 新题集（results/original30/）；review = 审稿后补充实验（results/review/）")
    ap.add_argument("--pilot", action="store_true", help=f"每组只跑 {PILOT_LIMIT} 题，输出到 <结果目录>/pilot/")
    ap.add_argument("--only", help="只运行名称匹配该正则的组（所需的第 0 轮自动包含）")
    ap.add_argument("-p", "--parallel", type=int, default=1, help="同时运行的组数")
    ap.add_argument("-j", "--workers", type=int, default=4, help="每组内部的并发题数（传给 repair.py）")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true", help="只检查，不运行")
    args = ap.parse_args()

    r0_jobs, rep_jobs = select(*expand_matrix(args.matrix), args.only)
    base = out_dir(args.pilot, args.matrix)
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
