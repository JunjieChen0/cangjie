"""Original-30 留出测试评测（docs/留出测试评测方案.md）。不调用模型 API。

  python src/heldout_eval.py run [-j 8]   # 本机重跑原测试与留出测试，写 results/heldout/rows.jsonl（可续跑）
  python src/heldout_eval.py stats        # 只读 rows.jsonl，写 results/stats/heldout_stats.{md,json}（离线可复现）

同一份代码（按代码 + 题号 + 测试种类）只编译运行一次，结果缓存在 results/heldout/cache.jsonl。
"""
import argparse
import glob
import hashlib
import json
import os
import random
import statistics as st
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import ROOT, load_original30  # noqa: E402
from review_stats import REVIEW_TIMEOUT_AS_FAIL, bases, load_all, run_families  # noqa: E402
from run_matrix import N_TASKS  # noqa: E402
from stage3_stats import compare, load_groups, parse_name  # noqa: E402

HELD = os.path.join(ROOT, "data", "original30", "heldout_tests.jsonl")
HELD_SHA = "311567ce46a5330f90ac16890dd578f05c009b3730e68103c1f73731a1542bd2"
OUT = os.path.join(ROOT, "results", "heldout")
ROWS, CACHE = os.path.join(OUT, "rows.jsonl"), os.path.join(OUT, "cache.jsonl")
STATS = os.path.join(ROOT, "results", "stats", "heldout_stats")
BASES = {"original30": None, "review": REVIEW_TIMEOUT_AS_FAIL}   # 与 stage3_stats / review_stats 的纳入口径相同
MAX_TRIES = 3
AMBIGUOUS = frozenset({1014, 1022, 1027})
N_BOOT, SEED = 10000, 0


def check_hash() -> dict[int, str]:
    with open(HELD, "rb") as f:
        raw = f.read().replace(b"\r\n", b"\n")
    if hashlib.sha256(raw).hexdigest() != HELD_SHA:
        sys.exit("heldout_tests.jsonl 的 SHA-256 与方案不一致，停止")
    return {r["id"]: r["test"] for r in (json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip())}


def read_rows(path: str) -> dict[int, dict]:
    """同 load_groups：同一题有多行时，无错误的行优先。"""
    by_id: dict[int, dict] = {}
    with open(path, encoding="utf-8") as f:
        for r in (json.loads(x) for x in f if x.strip()):
            if "error" not in r or int(r["id"]) not in by_id:
                by_id[int(r["id"])] = r
    return by_id


def collect() -> list[dict]:
    """纳入的修复组（与现有统计相同的 load_groups 口径）与第 0 轮文件中的每个题次。"""
    items = []
    for sub, taf in BASES.items():
        base = os.path.join(ROOT, "results", sub)
        included = {(k, rep) for k, reps in load_groups(base, timeout_as_fail=taf).items() for rep in reps}
        for p in sorted(glob.glob(os.path.join(base, "runs", "*_or_*.jsonl"))):
            name = os.path.basename(p)[:-len(".jsonl")]
            parsed = parse_name(name)
            if parsed is None or (parsed[:4], parsed[4]) not in included:
                continue
            items += [{"file": f"{sub}/runs/{name}", "group": "_".join(parsed[:4]), "rep": parsed[4], "id": i,
                       "rounds_used": r.get("rounds_used", 0), "code": r.get("solution")}
                      for i, r in read_rows(p).items()]
        for p in sorted(glob.glob(os.path.join(base, "r0", "*_or_*_r0.jsonl"))):
            name = os.path.basename(p)[:-len(".jsonl")]
            with open(p[:-len(".jsonl")] + ".summary.json", encoding="utf-8") as f:
                s = json.load(f)
            if s.get("n") != 30 or s.get("errors") != 0:
                print(f"跳过第 0 轮文件（n={s.get('n')}, errors={s.get('errors')}）：{sub}/r0/{name}")
                continue
            items += [{"file": f"{sub}/r0/{name}", "group": name, "rep": 0, "id": i, "rounds_used": 0,
                       "code": r.get("solution")} for i, r in read_rows(p).items()]
    return items


def job_key(code: str, pid: int, kind: str) -> str:
    return hashlib.sha256(f"{kind}\0{pid}\0{code}".encode("utf-8")).hexdigest()


def run_one(src: str) -> dict:
    """超时重跑，最多共 MAX_TRIES 次，取最后一次。"""
    from runner import compile_and_run
    for tries in range(1, MAX_TRIES + 1):
        r = compile_and_run(src)
        if r.failure_kind != "timeout":
            break
    return {"passed": bool(r.passed), "timeouts": tries - (r.failure_kind != "timeout"),
            "failure_kind": r.failure_kind}


def cmd_run(jobs: int) -> None:
    held, probs = check_hash(), load_original30()
    items = collect()
    os.makedirs(OUT, exist_ok=True)
    cache = {}
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            cache = {c["key"]: c for c in (json.loads(x) for x in f if x.strip())}
    todo = {}
    for it in items:
        if it["code"]:
            for kind, test in (("O", probs[it["id"]]["test"]), ("H", held[it["id"]])):
                k = job_key(it["code"], it["id"], kind)
                if k not in cache:
                    todo[k] = it["code"] + "\n" + test       # 拼接方式同 repair.evaluate
    print(f"题次 {len(items)}；需编译运行 {len(todo)}（已缓存 {len(cache)}）", flush=True)
    with open(CACHE, "a", encoding="utf-8", newline="\n") as f, ThreadPoolExecutor(jobs) as ex:
        futs = {ex.submit(run_one, src): k for k, src in todo.items()}
        for n, fut in enumerate(as_completed(futs), 1):
            c = {"key": futs[fut], **fut.result()}
            cache[c["key"]] = c
            f.write(json.dumps(c) + "\n")
            f.flush()
            if n % 200 == 0:
                print(f"  {n}/{len(todo)}", flush=True)
    with open(ROWS, "w", encoding="utf-8", newline="\n") as f:
        for it in items:
            row = {k: it[k] for k in ("file", "group", "rep", "id", "rounds_used")}
            if it["code"]:
                o, h = (cache[job_key(it["code"], it["id"], k)] for k in ("O", "H"))
                row.update(O=o["passed"], H=h["passed"], timeouts=o["timeouts"] + h["timeouts"])
            else:
                row.update(O=False, H=False, timeouts=0, no_code=True)
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"写入 {ROWS}")


# ---------------- 统计（只读 rows.jsonl 与已有结果文件） ----------------

def fb_of(row: dict) -> str:
    return "r0" if row["file"].split("/")[1] == "r0" else row["group"].rsplit("_", 1)[1]


def fail_rates(rows: list[dict], weights: dict[int, int] | None = None) -> tuple:
    """(修复通过的留出失败率, 第 0 轮通过的留出失败率, 差, 计数)，百分点；weights 为 bootstrap 中各题被抽中的次数。"""
    c = [0, 0, 0, 0]          # 修复失败, 修复通过数, 第 0 轮失败, 第 0 轮通过数
    for r in rows:
        if not r["O"]:
            continue
        w = 1 if weights is None else weights.get(r["id"], 0)
        j = 0 if r["rounds_used"] >= 1 else 2
        c[j] += w * (not r["H"])
        c[j + 1] += w
    a = 100 * c[0] / c[1] if c[1] else float("nan")
    b = 100 * c[2] / c[3] if c[3] else float("nan")
    return a, b, a - b, c


def boot_diff(rows: list[dict]) -> tuple[float, float]:
    """按题整群 bootstrap（每次重抽全部题目，seed 0）；某次抽样中某类为空时丢弃该次。"""
    ids = sorted({r["id"] for r in rows})
    rng = random.Random(SEED)
    boots = []
    for _ in range(N_BOOT):
        w: dict[int, int] = defaultdict(int)
        for _ in ids:
            w[rng.choice(ids)] += 1
        boots.append(fail_rates(rows, w)[2])
    boots = sorted(x for x in boots if x == x)
    return boots[int(0.025 * len(boots))], boots[min(int(0.975 * len(boots)), len(boots) - 1)]


def primary(rows: list[dict]) -> dict:
    a, b, d, c = fail_rates(rows)
    lo, hi = boot_diff(rows)
    return {"repaired_fail_pct": round(a, 2), "r0_fail_pct": round(b, 2), "diff_pp": round(d, 2),
            "ci_lo": round(lo, 2), "ci_hi": round(hi, 2), "repaired_fail": c[0], "repaired_n": c[1],
            "r0_fail": c[2], "r0_n": c[3], "n_tasks": len({r["id"] for r in rows})}


def verdict(p: dict) -> str:
    if p["ci_lo"] <= 0 <= p["ci_hi"]:
        return "未检出修复拟合反馈测试的证据"
    if p["ci_lo"] > 0:
        return f"修复得到的通过中，有 {p['repaired_fail_pct']}% 在留出测试上失败，高于第 0 轮通过的 {p['r0_fail_pct']}%"
    return "修复通过的留出失败率低于第 0 轮通过（如实报告，不作额外解释）"


def per_group(rows: list[dict]) -> list[dict]:
    reps: dict[str, dict[tuple, list]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        reps[r["group"]][(r["file"], r["rep"])].append(r)
    out = []
    for g, by_rep in sorted(reps.items()):
        o = [100 * sum(x["O"] for x in v) / len(v) for v in by_rep.values()]
        oh = [100 * sum(x["O"] and x["H"] for x in v) / len(v) for v in by_rep.values()]
        sd = (lambda xs: round(st.stdev(xs), 2) if len(xs) > 1 else 0.0)
        out.append({"group": g, "runs": len(by_rep), "O_pct": round(st.mean(o), 2), "O_sd": sd(o),
                    "OH_pct": round(st.mean(oh), 2), "OH_sd": sd(oh)})
    return out


def by_feedback(rows: list[dict]) -> list[dict]:
    out = []
    for fb in sorted({fb_of(r) for r in rows} - {"r0"}):
        rep = [r for r in rows if fb_of(r) == fb and r["O"] and r["rounds_used"] >= 1]
        f = sum(not r["H"] for r in rep)
        out.append({"feedback": fb, "repaired_n": len(rep), "heldout_fail": f,
                    "fail_pct": round(100 * f / len(rep), 2) if rep else None})
    return out


def recompare(rows: list[dict]) -> dict:
    """以「本机原测试与留出测试都通过」为结果，按原方法、原比较族与 Holm 方式重算 Original-30 的已有比较。"""
    oh: dict[str, dict[str, bool]] = {}
    for r in rows:
        if "/runs/" in r["file"]:
            oh.setdefault(r["file"], {})[str(r["id"])] = bool(r["O"] and r["H"])

    def swap(key: tuple, reps: dict, sub: str) -> None:
        for rep, d in reps.items():
            d["passed"] = oh[f"{sub}/runs/{'_'.join(key)}_rep{rep}"]     # 缺失即报错，不静默置空

    o30 = load_groups(os.path.join(ROOT, "results", "original30"))
    for key, reps in o30.items():
        swap(key, reps, "original30")
    review, olds = bases(False)
    groups = load_all(review, olds, N_TASKS)
    for key, reps in groups.items():          # load_all 中 Original-30 的组来自 review，或（复用模型）来自 original30
        if key[1] == "or":
            in_review = os.path.exists(os.path.join(review, "runs", "_".join(key) + f"_rep{min(reps)}.jsonl"))
            swap(key, reps, "review" if in_review else "original30")
    return {"original30": compare(o30), "review_or": [r for r in run_families(groups) if r["ds"] == "or"]}


def cmd_stats() -> None:
    with open(ROWS, encoding="utf-8") as f:
        rows = [json.loads(x) for x in f if x.strip()]
    main_ = primary(rows)
    recorded = {}
    for p in {r["file"] for r in rows}:
        recorded.update({(p, i): bool(x["passed"]) for i, x in
                         read_rows(os.path.join(ROOT, "results", p + ".jsonl")).items()})
    res = {"primary": {**main_, "verdict": verdict(main_)},
           "drop_ambiguous": primary([r for r in rows if r["id"] not in AMBIGUOUS]),
           "n_rows": len(rows), "no_code": sum(bool(r.get("no_code")) for r in rows),
           "timeout_rows": sum(r["timeouts"] > 0 for r in rows),
           "O_vs_recorded_agree": sum(recorded[(r["file"], r["id"])] == r["O"] for r in rows),
           "by_feedback": by_feedback(rows), "recompare": recompare(rows), "per_group": per_group(rows),
           "heldout_sha256": HELD_SHA, "n_boot": N_BOOT, "seed": SEED}
    os.makedirs(os.path.dirname(STATS), exist_ok=True)
    with open(STATS + ".json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with open(STATS + ".md", "w", encoding="utf-8", newline="\n") as f:
        f.write(render(res))
    print(render(res))


def render(res: dict) -> str:
    p, s = res["primary"], res["drop_ambiguous"]
    L = ["# Original-30 留出测试评测（方案见 docs/留出测试评测方案.md）", "",
         f"题次 {res['n_rows']}（无代码 {res['no_code']}，出现超时 {res['timeout_rows']}）；"
         f"本机原测试与记录中 `passed` 一致 {res['O_vs_recorded_agree']}/{res['n_rows']}。", "",
         "## 主要分析", "",
         "| 范围 | 修复通过的留出失败率 | 第 0 轮通过的留出失败率 | 差（百分点） | 95% CI |", "|---|---|---|---|---|"]
    for name, x in (("全部 30 题", p), ("去掉 1014、1022、1027", s)):
        L.append(f"| {name} | {x['repaired_fail_pct']}%（{x['repaired_fail']}/{x['repaired_n']}） | "
                 f"{x['r0_fail_pct']}%（{x['r0_fail']}/{x['r0_n']}） | {x['diff_pp']:+.2f} | "
                 f"[{x['ci_lo']:+.2f}, {x['ci_hi']:+.2f}] |")
    L += ["", f"结论（按预先约定的写法）：{p['verdict']}。", "",
          "## 按反馈方式（修复通过的留出失败率，只做描述）", "",
          "| 反馈 | 修复通过题次 | 留出失败 | 失败率 |", "|---|---|---|---|"]
    L += [f"| {x['feedback']} | {x['repaired_n']} | {x['heldout_fail']} | {x['fail_pct']}% |" for x in res["by_feedback"]]
    L += ["", "## 以「原测试与留出测试都通过」重算已有比较（敏感性分析）", "",
          "| 来源 | 族 | 模型 | 起点 | A vs B | 差 | 95% CI | p(Holm) |", "|---|---|---|---|---|---|---|---|"]
    for src, rows in res["recompare"].items():
        L += [f"| {src} | {r.get('family', '-')} | {r['model']} | {r['prompt']} | {r['a']} vs {r['b']} | {r['diff']:+.2f} | "
              f"[{r['ci_lo']:+.2f}, {r['ci_hi']:+.2f}] | {r['p_holm']:.4f} |" for r in rows]
    L += ["", "## 每组通过率（本机原测试 O；原测试与留出测试都通过 O&H；均值 ± 标准差）", "",
          "| 组 | 次数 | O | O&H |", "|---|---|---|---|"]
    L += [f"| {g['group']} | {g['runs']} | {g['O_pct']} ± {g['O_sd']} | {g['OH_pct']} ± {g['OH_sd']} |"
          for g in res["per_group"]]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "stats"))
    ap.add_argument("-j", type=int, default=8)
    a = ap.parse_args()
    cmd_run(a.j) if a.cmd == "run" else cmd_stats()
