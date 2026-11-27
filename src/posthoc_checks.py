"""修订方案（docs/修订实验方案.md）第八节：零成本的事后分析。

主结果都已看过，以下一律为事后 / 探索性分析，不改变任何预先设定的判定；只读结果文件，不调用模型：
1. 交互效应的天花板检验：syntax × hint 交互只在 direct 与 syntax 两个起点第 0 轮都失败的题上重算
   （第 0 轮已通过的题两种反馈之差恒为 0，若 syntax 起点第 0 轮通过的题更多，交互可能只是天花板造成的）。
2. rag2 离线选优的对半验证：150 个查询随机对半（seed 0），在一半上按 hit@3（平局看 nDCG@3）选检索器，
   在另一半上报告选中方案相对 BM25 的 hit@3 / nDCG@3；两个方向都做，另附 1,000 次随机对半的选中频率。
   选型规则是这里事后写定的（原选型未成文，rewrite_hybrid_rerank 当时在三项指标上都最高）。
3. hint 规则来源：规则在 HumanEval 全部 164 题的公开失败样本上挖掘，无法追溯到个别题；
   ClassEval 与 Original-30 不在挖掘范围内，列出这两个数据集上已有的 hint vs raw 比较作为留出集结果。
4. 比较族划分对照：各族分别 Holm、G / A / R 合并 Holm、全部（含交互）合并 Holm 的显著数并列。
5. 延迟：日志中没有逐次调用的时间，只在报告中说明（不计算）。

须先运行 stage3_stats.py（含 --matrix original）与 review_stats.py：
  python src/posthoc_checks.py     # → results/stats/posthoc_checks.{md,json}
"""
from __future__ import annotations

import glob
import json
import os
import random
import re
import statistics as st
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import retrieval_eval as RE  # noqa: E402
import review_stats as R  # noqa: E402
from data import BENCH_DIR  # noqa: E402
from extra_stats import bootstrap_ci, fmt_p, holm  # noqa: E402
from run_matrix import N_TASKS  # noqa: E402

ALPHA = 0.05
OUT = os.path.join(R.RESULTS, "stats")
EVAL = os.path.join(R.RESULTS, "retrieval_eval")
RUN_BASES = tuple(os.path.join(R.RESULTS, d) for d in ("review", "stage3", "original30"))  # 与 load_all 的取数顺序一致
R0_DIRS = tuple(os.path.join(b, "r0") for b in RUN_BASES)
_R0_NAME = re.compile(r"^(.+?)_(he|ce|or)_(direct|syntax)_r0\.jsonl$")
STARTS, ARMS = ("direct", "syntax"), ("hint", "raw")
BASELINE = "bm25"
SPLIT_SEED, N_SPLITS = 0, 1000
FAMILY_ORDER = ("G", "A", "R", "I", "I-explore")
# hint 规则的来源（git log --follow src/repair_hints.py：只有初始提交，之后未改动）
RULES_COMMIT = ("42665cc", "2026-11-16")
ORIGINAL30_COMMIT = ("ba92a68", "2026-11-17")      # Original-30 数据集加入仓库的提交
STATS_SOURCES = {"stage3": "stage3_stats.json", "original30": "original30_stats.json", "review": "review_stats.json"}


# ---------------------------------------------------------------- 1. 天花板检验
def load_r0(dirs: tuple[str, ...] = R0_DIRS) -> dict[tuple, frozenset]:
    """{(模型, 数据集, 起点): 第 0 轮通过的题号}；同一格在多个目录都有时取靠前的目录。"""
    out = {}
    for d in reversed(dirs):
        for p in glob.glob(os.path.join(d, "*_r0.jsonl")):
            m = _R0_NAME.match(os.path.basename(p))
            if m:
                out[m.groups()] = frozenset(i for i, r in R._rows(p).items() if r.get("passed"))
    return out


def _cells(groups: dict[tuple, dict]) -> list[tuple]:
    return [k for k in groups if k[2] in STARTS and k[3] in ARMS]


def _read_rep(key: tuple, rep: int, bases: tuple[str, ...] = RUN_BASES) -> dict[str, dict]:
    """一次重复的逐题记录（与 load_all 相同的目录顺序，取第一个存在的文件）。"""
    name = f"{'_'.join(key)}_rep{rep}.jsonl"
    for b in bases:
        p = os.path.join(b, "runs", name)
        if os.path.exists(p):
            return R._rows(p)
    raise FileNotFoundError(name)


def run_r0(groups: dict[tuple, dict], read=_read_rep) -> dict[tuple, list[frozenset]]:
    """{(模型, 数据集, 起点): [每个 hint / raw 组每次重复中第 0 轮判定通过（passed 且 rounds_used = 0）的题]}。
    第 0 轮代码共享，但每次运行都重新编译、测试，判定不稳定的题与 cjc 超时会让结果与第 0 轮文件不同。
    每次重复由逐题记录重算的 R0 须等于 summary 的第 0 轮通过率（确认读到的是统计所用的文件），否则报错。"""
    out: dict[tuple, list] = defaultdict(list)
    for key in _cells(groups):
        for rep, g in groups[key].items():
            rows = read(key, rep)
            ok = frozenset(i for i, r in rows.items() if r.get("passed") and r.get("rounds_used") == 0)
            if round(100 * len(ok) / len(rows), 2) != g["curve"][0]:
                raise ValueError(f"{'_'.join(key)}_rep{rep}：逐题记录的 R0 与 summary 不一致")
            out[key[:3]].append(ok)
    return dict(out)


def merge_r0(from_file: dict[tuple, frozenset], from_runs: dict[tuple, list[frozenset]]) -> tuple[dict, dict]:
    """第 0 轮通过 = 第 0 轮文件或任一次运行判定通过（保守：只要可能有天花板就去掉）；
    另返回判定不一致（文件与各次运行中有的通过、有的未通过）的题数。"""
    merged, differ = {}, {}
    for k in set(from_file) | set(from_runs):
        sets = ([from_file[k]] if k in from_file else []) + from_runs.get(k, [])
        merged[k] = frozenset().union(*sets)
        differ[k] = len(merged[k] - frozenset.intersection(*sets))
    return merged, differ


def ceiling_groups(groups: dict[tuple, dict], r0: dict[tuple, frozenset]) -> dict[tuple, dict]:
    """hint / raw 组只保留同一（模型, 数据集）下 direct 与 syntax 第 0 轮都失败的题（返回新字典，不改动输入）。"""
    out = {}
    for key in _cells(groups):
        both = [r0.get((key[0], key[1], s)) for s in STARTS]
        if any(x is None for x in both):
            continue
        drop = both[0] | both[1]
        out[key] = {rep: {**g, "passed": {i: v for i, v in g["passed"].items() if i not in drop}}
                    for rep, g in groups[key].items()}
    return out


def ceiling_check(groups: dict[tuple, dict], r0_file: dict[tuple, frozenset], main: list[dict]) -> list[dict]:
    r0, differ = merge_r0(r0_file, run_r0(groups))
    base = {(r["model"], r["ds"]): r for r in main}
    rows = []
    for r in R.interaction(ceiling_groups(groups, r0)):
        m = base[(r["model"], r["ds"])]
        d, s = (r0[(r["model"], r["ds"], p)] for p in STARTS)
        rows.append({**r, "n_all": m["n"], "interaction_all": m["interaction"], "p_holm_all": m["p_holm"],
                     "n_syntax_only_r0": len(s - d), "n_direct_only_r0": len(d - s),
                     "n_r0_verdict_differs": sum(differ[(r["model"], r["ds"], p)] for p in STARTS)})
    return rows


# ---------------------------------------------------------------- 2. rag2 对半验证
def _jsonl(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_retrieval(eval_dir: str = EVAL) -> list[dict]:
    """由 queries.jsonl（各检索器 top-3 片段标题）与 judgments.jsonl（片段分数）重建每条查询的指标。
    同一查询内标题唯一、同标题分数一致（已核对），重建结果须与 report.json 完全相同（见测试）。"""
    scores: dict[str, dict[str, int]] = defaultdict(dict)
    for j in _jsonl(os.path.join(eval_dir, "judgments.jsonl")):
        scores[j["qid"]][j["title"]] = j["score"] or 0
    out = []
    for q in _jsonl(os.path.join(eval_dir, "queries.jsonl")):
        judged = {t: scores[q["qid"]][t] for ts in q["results"].values() for t in ts}
        out.append({"qid": q["qid"], "category": q["category"], "metrics": RE.metrics(q["results"], judged)})
    return out


def _mean(rows: list[dict], name: str, key: str) -> float:
    return 100 * sum(r["metrics"][name][key] for r in rows) / len(rows)


def select(rows: list[dict]) -> str:
    """hit@3 最高的检索器，平局看 nDCG@3，再平局取 RETRIEVERS 中靠前的。"""
    return max(RE.RETRIEVERS, key=lambda n: (_mean(rows, n, "hit"), _mean(rows, n, "ndcg")))


def halves(qids: list[str], seed: int) -> tuple[list[str], list[str]]:
    ids = sorted(qids)
    random.Random(seed).shuffle(ids)
    h = len(ids) // 2
    return ids[:h], ids[h:]


def _held_out(sel: list[dict], test: list[dict], direction: str) -> dict:
    pick = select(sel)
    out = {"direction": direction, "selected": pick, "n_select": len(sel), "n_test": len(test)}
    for key in ("hit", "ndcg"):
        diffs = [r["metrics"][pick][key] - r["metrics"][BASELINE][key] for r in test]
        mean, lo, hi = bootstrap_ci(diffs)
        out |= {f"{key}_selected": round(_mean(test, pick, key), 1), f"{key}_baseline": round(_mean(test, BASELINE, key), 1),
                f"{key}_diff": round(mean, 1), f"{key}_ci": [round(lo, 1), round(hi, 1)]}
    return out


def split_half(rows: list[dict], seed: int = SPLIT_SEED) -> list[dict]:
    by = {r["qid"]: r for r in rows}
    a, b = ([by[q] for q in h] for h in halves(list(by), seed))
    return [_held_out(a, b, "A→B"), _held_out(b, a, "B→A")]


def repeated_splits(rows: list[dict], n: int = N_SPLITS) -> dict:
    """seed 1..n 的随机对半，每次两个方向：被选中的检索器频率，留出半区相对 BM25 的平均增益。"""
    by = {r["qid"]: r for r in rows}
    picks, gains = Counter(), {"hit": [], "ndcg": []}
    for seed in range(1, n + 1):
        a, b = ([by[q] for q in h] for h in halves(list(by), seed))
        for sel, test in ((a, b), (b, a)):
            pick = select(sel)
            picks[pick] += 1
            for key in gains:
                gains[key].append(_mean(test, pick, key) - _mean(test, BASELINE, key))
    return {"n_splits": n, "n_evaluations": 2 * n, "selected": dict(picks.most_common()),
            "hit_gain_mean": round(st.mean(gains["hit"]), 1), "ndcg_gain_mean": round(st.mean(gains["ndcg"]), 1),
            "share_hit_gain_positive": round(100 * sum(g > 0 for g in gains["hit"]) / (2 * n), 1)}


# ---------------------------------------------------------------- 3. hint 规则来源
def mining_pool(bench_dir: str = BENCH_DIR) -> dict | None:
    """mine_errors.py 的挖掘范围：CangjieBench 公开 HumanEval 评测记录中的失败样本（没有 CangjieBench 时返回 None）。"""
    import mine_errors
    results = os.path.join(bench_dir, "Results")
    if not os.path.isdir(results):
        return None
    he = glob.glob(os.path.join(results, "**", "*HumanEval*.records.jsonl"), recursive=True)
    ce = glob.glob(os.path.join(results, "**", "*ClassEval*.records.jsonl"), recursive=True)
    return {"humaneval_files": len(he), "humaneval_failures": sum(1 for _ in mine_errors.iter_stderr(he)),
            "classeval_files_not_mined": len(ce)}


def heldout_hint(stats: dict[str, dict]) -> list[dict]:
    """未参与规则挖掘的数据集（ClassEval、Original-30）上已有的 hint vs raw 比较；review 只取族 G。"""
    out = []
    for source, res in stats.items():
        for r in res["comparisons"]:
            if (r["a"], r["b"]) == ("hint", "raw") and r["ds"] != "he" and r.get("family", "G") == "G":
                out.append({"source": source} | {k: r[k] for k in ("model", "ds", "prompt", "n", "diff", "ci_lo",
                                                                  "ci_hi", "p_holm")})
    return out


# ---------------------------------------------------------------- 4. 比较族划分
def family_table(comps: list[dict], inter: list[dict]) -> list[dict]:
    """sig_within：族内 Holm；sig_gar：G / A / R 合并 Holm（review_stats 的 p_holm_all，交互族为 None）；
    sig_all：全部比较与交互合并后做一次 Holm。"""
    rows = comps + inter
    p_all = holm([r["p"] for r in rows])
    out = []
    for fam in FAMILY_ORDER:
        idx = [i for i, r in enumerate(rows) if r["family"] == fam]
        if not idx:
            continue
        gar = None if fam.startswith("I") else sum(rows[i]["p_holm_all"] < ALPHA for i in idx)
        out.append({"family": fam, "n": len(idx), "sig_within": sum(rows[i]["p_holm"] < ALPHA for i in idx),
                    "sig_gar": gar, "sig_all": sum(p_all[i] < ALPHA for i in idx)})
    return out


# ---------------------------------------------------------------- 主流程
def _load_stats() -> dict[str, dict]:
    out = {}
    for source, name in STATS_SOURCES.items():
        with open(os.path.join(OUT, name), encoding="utf-8") as f:
            out[source] = json.load(f)
    return out


def run() -> dict:
    stats = _load_stats()
    review, olds = R.bases(False)
    groups = R.load_all(review, olds, N_TASKS)
    rows = load_retrieval()
    with open(os.path.join(EVAL, "report.json"), encoding="utf-8") as f:
        reproduced = RE.summarize(rows) == json.load(f)["summary"]
    return {"ceiling": ceiling_check(groups, load_r0(), stats["review"]["interaction"]),
            "rag2_split": {"reproduces_report": reproduced, "n_queries": len(rows), "seed": SPLIT_SEED,
                           "split_half": split_half(rows), "repeated": repeated_splits(rows)},
            "hint_provenance": {"rules_commit": RULES_COMMIT, "original30_commit": ORIGINAL30_COMMIT,
                                "mining_pool": mining_pool(), "heldout": heldout_hint(stats)},
            "families": family_table(stats["review"]["comparisons"], stats["review"]["interaction"])}


def _ceiling_md(rows: list[dict]) -> list[str]:
    L = ["## 1. 交互效应的天花板检验", "",
         "只保留 direct 与 syntax 两个起点第 0 轮都失败的题，按 review_stats 的同一方法（按题差值、bootstrap CI、"
         "符号翻转置换检验、I 与 I-explore 各自 Holm）重算 I = (hint − raw)<sub>direct</sub> − (hint − raw)<sub>syntax</sub>。",
         "第 0 轮代码在同一格内共享，但每次运行都重新编译、测试；判定不稳定的题（如 HumanEval 20）与 cjc 超时会让个别题的"
         "第 0 轮判定与第 0 轮文件不同。这里取保守口径：第 0 轮文件或任一 hint / raw 运行中第 0 轮判定通过，即视为第 0 轮通过并去掉。"
         "「判定不一致」为两个起点中第 0 轮文件与各次运行的判定不全相同的题数之和；「仅 syntax 第 0 轮通过」即只在 syntax 起点有天花板的题数。", "",
         "| 族 | 模型 | 数据集 | 全部题：题数 / I / p(Holm) | 仅 syntax 第 0 轮通过 | 仅 direct 第 0 轮通过 | 判定不一致 | "
         "都失败：题数 / I [95% CI] / p(Holm) |", "|---|---|---|---|---:|---:|---:|---|"]
    L += [f"| {r['family']} | {r['model']} | {r['ds']} | {r['n_all']} / {r['interaction_all']:+.2f} / "
          f"{fmt_p(r['p_holm_all'])} | {r['n_syntax_only_r0']} | {r['n_direct_only_r0']} | {r['n_r0_verdict_differs']} | {r['n']} / "
          f"{r['interaction']:+.2f} [{r['ci_lo']:+.2f}, {r['ci_hi']:+.2f}] / {fmt_p(r['p_holm'])} |" for r in rows]
    return L + [""]


def _rag2_md(res: dict) -> list[str]:
    L = ["## 2. rag2 离线选优的对半验证", "",
         f"{res['n_queries']} 个查询（重建的逐条指标{'与 report.json 完全一致' if res['reproduces_report'] else '与 report.json 不一致！'}）"
         f"按 seed {res['seed']} 随机对半；在选型半区按 hit@3（平局看 nDCG@3）选检索器，在另一半报告。"
         "差值 = 选中方案 − BM25（百分点），95% CI 为按查询 bootstrap（seed 0，10,000 次）。选型规则为事后写定。", "",
         "| 方向 | 选型 / 留出题数 | 选中 | hit@3：选中 / BM25 / 差值 [95% CI] | nDCG@3：选中 / BM25 / 差值 [95% CI] |",
         "|---|---|---|---|---|"]
    for r in res["split_half"]:
        L.append(f"| {r['direction']} | {r['n_select']} / {r['n_test']} | {r['selected']} | "
                 f"{r['hit_selected']} / {r['hit_baseline']} / {r['hit_diff']:+.1f} [{r['hit_ci'][0]:+.1f}, {r['hit_ci'][1]:+.1f}] | "
                 f"{r['ndcg_selected']} / {r['ndcg_baseline']} / {r['ndcg_diff']:+.1f} "
                 f"[{r['ndcg_ci'][0]:+.1f}, {r['ndcg_ci'][1]:+.1f}] |")
    rep = res["repeated"]
    L += ["", f"另做 {rep['n_splits']:,} 次随机对半（seed 1–{rep['n_splits']}，每次两个方向，共 {rep['n_evaluations']:,} 次选型）："
          "选中频率 " + "、".join(f"{k} {v}" for k, v in rep["selected"].items()) +
          f"；留出半区相对 BM25 的平均增益 hit@3 {rep['hit_gain_mean']:+.1f}、nDCG@3 {rep['ndcg_gain_mean']:+.1f} 个百分点，"
          f"hit@3 增益为正的占 {rep['share_hit_gain_positive']}%。", ""]
    return L


def _hint_md(res: dict) -> list[str]:
    pool = res["mining_pool"]
    pool_txt = (f"CangjieBench 公开 HumanEval 评测记录 {pool['humaneval_files']} 个文件中的 {pool['humaneval_failures']:,} 个失败样本"
                f"（同目录 {pool['classeval_files_not_mined']} 个 ClassEval 记录文件不在扫描范围内）"
                if pool else "CangjieBench 公开 HumanEval 评测记录中的失败样本（本机没有 CangjieBench，未重新计数）")
    L = ["## 3. hint 规则来源", "",
         f"- `src/repair_hints.py` 的 16 条规则只在初始提交 {res['rules_commit'][0]}（{res['rules_commit'][1]}）中出现，之后未改动；"
         f"挖掘范围（`mine_errors.py`）为{pool_txt}。",
         "- 这些样本覆盖 HumanEval 全部 164 题、来自多个模型；规则按报错模板归纳，没有记录由哪些题构建，"
         "因此**无法**在 HumanEval 内划出「未参与构建的题」（Dev / Test 对半见 extra_stats.md 第 1 节，同样不是严格留出）。",
         f"- ClassEval 不在挖掘范围内；Original-30 在规则冻结之后才加入仓库（{res['original30_commit'][0]}，"
         f"{res['original30_commit'][1]}）。下表为这两个数据集上已有的 hint vs raw 比较（数字取自各统计文件，p(Holm) 为原文件中的校正口径），"
         "可视为对规则的留出评估。", "",
         "| 来源 | 模型 | 数据集 | 起点 | 题数 | hint − raw [95% CI] | p(Holm) |", "|---|---|---|---|---:|---|---|"]
    L += [f"| {r['source']} | {r['model']} | {r['ds']} | {r['prompt']} | {r['n']} | "
          f"{r['diff']:+.2f} [{r['ci_lo']:+.2f}, {r['ci_hi']:+.2f}] | {fmt_p(r['p_holm'])} |" for r in res["heldout"]]
    pos = [r for r in res["heldout"] if r["p_holm"] < ALPHA and r["diff"] > 0]
    neg = [r for r in res["heldout"] if r["p_holm"] < ALPHA and r["diff"] < 0]
    return L + ["", f"{len(res['heldout'])} 个比较中 Holm 后显著为正 {len(pos)} 个、显著为负 {len(neg)} 个。", ""]


def _family_md(rows: list[dict]) -> list[str]:
    L = ["## 4. 比较族划分对照", "",
         f"显著 = 校正后 p < {ALPHA}。族内：预先设定的划分（主结论口径）；G+A+R 合并：review_stats 中的敏感性口径；"
         "全部合并：G / A / R 的全部比较与两个交互族一起做一次 Holm。族 B（调用预算）待修订实验完成后加入。", "",
         "| 族 | 比较数 | 族内 Holm | G+A+R 合并 Holm | 全部合并 Holm |", "|---|---:|---:|---:|---:|"]
    L += [f"| {r['family']} | {r['n']} | {r['sig_within']} | {'—' if r['sig_gar'] is None else r['sig_gar']} | "
          f"{r['sig_all']} |" for r in rows]
    tot = {k: sum(r[k] or 0 for r in rows) for k in ("n", "sig_within", "sig_gar", "sig_all")}
    return L + [f"| 合计 | {tot['n']} | {tot['sig_within']} | {tot['sig_gar']}（不含交互） | {tot['sig_all']} |", ""]


LATENCY_MD = ["## 5. 延迟", "",
              "记录（*.jsonl）与 summary 中没有逐次调用的时间戳；日志只有 tqdm 进度条给出的每组总耗时，"
              "它同时受并发数（-j）、同时运行的组数（-p）、运行主机、cjc 编译与 API 重试影响，不能当作调用延迟。"
              "按方案第八节第 5 条，不报告延迟，在论文局限性中说明。", ""]


def write_markdown(res: dict, path: str) -> None:
    L = ["# 零成本事后分析（自动生成）", "",
         "对应 docs/修订实验方案.md 第八节。主结果都已看过，以下全部为事后 / 探索性分析，不改变任何预先设定的判定；"
         "只读结果文件，不调用模型。", ""]
    L += _ceiling_md(res["ceiling"]) + _rag2_md(res["rag2_split"]) + _hint_md(res["hint_provenance"])
    L += _family_md(res["families"]) + LATENCY_MD
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def main():
    res = run()
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "posthoc_checks.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    write_markdown(res, os.path.join(OUT, "posthoc_checks.md"))
    print(f"天花板检验 {len(res['ceiling'])} 格；rag2 复现 report.json：{res['rag2_split']['reproduces_report']}；"
          f"留出 hint 比较 {len(res['hint_provenance']['heldout'])} 个 → {OUT}/posthoc_checks.md")


if __name__ == "__main__":
    main()
