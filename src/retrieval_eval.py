"""检索方案离线评估：在第 2 阶段（results/exp、results/ablation）的修复反馈上比较多种检索器，选出 rag2 的方案。

不使用第 3 阶段与 review 正式实验的数据，选型结果在跑 review 实验前冻结。
需要在检索环境中运行（含 torch / sentence-transformers）：
  .venv-retrieval/Scripts/python.exe src/retrieval_eval.py            # 抽样 → 检索 → LLM 判定 → 报告
  .venv-retrieval/Scripts/python.exe src/retrieval_eval.py --per-cat 5 # 小规模试跑
输出 results/retrieval_eval/{rewrites,judgments,queries}.jsonl 与 report.{md,json}；向量缓存在 cache/（不进 git）。

检索器（每个返回 top-3 文档片段）：
  bm25                   现有 rag：doc_retrieval.build_query + BM25
  rewrite_bm25           先让 REWRITER 把报错改写成文档检索词，再 BM25
  dense                  bge-m3 向量检索（查询同 bm25）
  hybrid                 BM25 与 dense 各取前 50，倒数排名融合（RRF，k=60）
  hybrid_rerank          hybrid 前 20 用 bge-reranker-v2-m3 重排
  rewrite_hybrid_rerank  改写后的查询 + hybrid_rerank
判定：JUDGE 模型对每个（报错, 片段）独立打分：2 = 含修复所需的具体写法或 API，1 = 主题相关但不足以修复，0 = 无关。
指标：hit@3（top-3 中至少一个 2 分）、any@3（至少一个 ≥1 分）、nDCG@3（增益 = 分数，理想排序取该题全部被判定片段）。
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import random
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import classify_error  # noqa: E402
from doc_retrieval import build_query, get_index, query_tokens  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "retrieval_eval")
POOL = [os.path.join(ROOT, "results", d, "*.jsonl") for d in ("exp", "ablation")]
CATEGORIES = ("foreign_syntax", "api_or_undeclared", "type_or_mutability", "other_compile", "runtime_exception")
RETRIEVERS = ("bm25", "rewrite_bm25", "dense", "hybrid", "hybrid_rerank", "rewrite_hybrid_rerank")
K, FUSE_DEPTH, RERANK_DEPTH, RRF_K = 3, 50, 20, 60
MAX_TOKENS = 1024
EMBED_MODEL, RERANK_MODEL = "BAAI/bge-m3", "BAAI/bge-reranker-v2-m3"
REWRITER = "doubao-seed-2-0-mini-260428"
JUDGE = "deepseek-v4-pro-ga-260813"
SEED = 7

REWRITE_PROMPT = """You are helping search the official Cangjie programming language documentation.
Below is a Cangjie compiler or runtime error from a program. Write ONE short search query (at most 12 words) naming the
Cangjie language construct, standard-library type or API that the programmer needs to look up to fix it.
Output only the query.

Error:
{feedback}"""

JUDGE_PROMPT = """You judge documentation retrieval for repairing Cangjie programs.
Error message (with the offending source lines):
{feedback}

Documentation passage:
[{title}]
{text}

Score how useful this passage is for fixing the error:
2 = it shows the specific Cangjie construct, syntax or API needed to fix the error;
1 = it is on a related topic but does not by itself show the fix;
0 = unrelated.
Answer with a single digit."""


# ---------------------------------------------------------------- 抽样
def load_pool(patterns: list[str] = POOL) -> list[dict]:
    """第 2 阶段日志中给模型看过的反馈（每题最后一条之前），按报错原文去重。"""
    seen, items = set(), []
    for pat in patterns:
        for path in sorted(glob.glob(pat)):
            with open(path, encoding="utf-8") as f:
                for row in map(json.loads, f):
                    for h in row.get("history", [])[:-1]:
                        fb = h.get("feedback", "")
                        cat = classify_error(h)
                        if fb and cat in CATEGORIES and fb not in seen:
                            seen.add(fb)
                            items.append({"src": os.path.basename(path), "task": str(row.get("id")),
                                          "category": cat, "feedback": fb})
    return items


def sample_queries(pool: list[dict], per_cat: int, seed: int = SEED) -> list[dict]:
    """按类别分层抽样，每类至多 per_cat 条；qid 为报错原文的哈希（缓存按内容复用，与抽样规模无关）。"""
    rng = random.Random(seed)
    by_cat = defaultdict(list)
    for it in pool:
        by_cat[it["category"]].append(it)
    out = []
    for cat in CATEGORIES:
        out += rng.sample(by_cat[cat], min(per_cat, len(by_cat[cat])))
    return [dict(q, qid=hashlib.sha1(q["feedback"].encode("utf-8")).hexdigest()[:12]) for q in out]


# ---------------------------------------------------------------- 检索
def rrf(rankings: list[list[int]], k: int = RRF_K) -> list[int]:
    """倒数排名融合：score(d) = Σ 1 / (k + rank)，rank 从 1 开始；同分按首次出现顺序。"""
    score, first = defaultdict(float), {}
    for ranking in rankings:
        for r, d in enumerate(ranking, 1):
            score[d] += 1.0 / (k + r)
            first.setdefault(d, len(first))
    return sorted(score, key=lambda d: (-score[d], first[d]))


def bm25_rank(query: str, depth: int) -> list[int]:
    chunks, bm25 = get_index()
    s = bm25.scores(query_tokens(query))
    return [i for i in sorted(range(len(chunks)), key=lambda i: (-s[i], i))[:depth] if s[i] > 0]


class Dense:
    """bge-m3 向量检索与 bge-reranker 重排（按需加载，片段向量缓存到磁盘）。"""

    def __init__(self, cache_dir: str):
        import numpy as np
        from sentence_transformers import CrossEncoder, SentenceTransformer
        self.np = np
        chunks, _ = get_index()
        self.texts = [c["title"] + "\n" + c["text"] for c in chunks]
        self.embedder = SentenceTransformer(EMBED_MODEL, device="cuda")
        self.embedder.max_seq_length = MAX_TOKENS   # 默认 8192 会让长片段拖慢整批；片段平均约 520 字符
        path = os.path.join(cache_dir, f"chunk_emb_{len(chunks)}.npy")
        if os.path.exists(path):
            self.emb = np.load(path)
        else:
            os.makedirs(cache_dir, exist_ok=True)
            self.emb = self.embedder.encode(self.texts, batch_size=32, normalize_embeddings=True,
                                            show_progress_bar=True)
            np.save(path, self.emb)
        self.reranker = CrossEncoder(RERANK_MODEL, device="cuda", max_length=1024)

    def rank(self, query: str, depth: int) -> list[int]:
        q = self.embedder.encode([query], normalize_embeddings=True)[0]
        return [int(i) for i in self.np.argsort(-(self.emb @ q))[:depth]]

    def rerank(self, query: str, cand: list[int]) -> list[int]:
        scores = self.reranker.predict([(query, self.texts[i]) for i in cand])
        return [cand[i] for i in sorted(range(len(cand)), key=lambda i: -float(scores[i]))]


def run_retrievers(q: dict, dense: Dense, rewritten: str) -> dict[str, list[int]]:
    base = build_query(q["feedback"])

    def hybrid(query: str) -> list[int]:
        return rrf([bm25_rank(query, FUSE_DEPTH), dense.rank(query, FUSE_DEPTH)])

    return {"bm25": bm25_rank(base, K),
            "rewrite_bm25": bm25_rank(rewritten, K),
            "dense": dense.rank(base, K),
            "hybrid": hybrid(base)[:K],
            "hybrid_rerank": dense.rerank(base, hybrid(base)[:RERANK_DEPTH])[:K],
            "rewrite_hybrid_rerank": dense.rerank(rewritten, hybrid(rewritten)[:RERANK_DEPTH])[:K]}


# ---------------------------------------------------------------- 判定与指标
def parse_score(text: str) -> int | None:
    m = re.search(r"[012]", text or "")
    return int(m.group(0)) if m else None


def _dcg(scores: list[int]) -> float:
    return sum(s / math.log2(i + 2) for i, s in enumerate(scores))


def metrics(results: dict[str, list[int]], judged: dict[int, int]) -> dict[str, dict]:
    """results：检索器 → top-K 片段编号；judged：片段编号 → 分数（该题所有检索器结果的并集）。"""
    ideal = _dcg(sorted(judged.values(), reverse=True)[:K])
    out = {}
    for name, ids in results.items():
        s = [judged.get(i, 0) for i in ids[:K]]
        out[name] = {"hit": int(2 in s), "any": int(any(s)), "ndcg": _dcg(s) / ideal if ideal else 0.0}
    return out


def summarize(per_query: list[dict]) -> dict:
    """per_query：[{category, metrics: {检索器: {hit, any, ndcg}}}] → 总体与分类别均值（百分比，一位小数）。"""
    def mean(rows, name, key):
        return round(100 * sum(r["metrics"][name][key] for r in rows) / len(rows), 1) if rows else None
    groups = {"all": per_query, **{c: [r for r in per_query if r["category"] == c] for c in CATEGORIES}}
    return {g: {"n": len(rows), **{n: {k: mean(rows, n, k) for k in ("hit", "any", "ndcg")} for n in RETRIEVERS}}
            for g, rows in groups.items()}


# ---------------------------------------------------------------- 主流程
def _cached_jsonl(path: str, key) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return {key(r): r for r in map(json.loads, f)}


def _parallel_append(fn, items, path: str, workers: int) -> list[dict]:
    """并发执行 fn，结果逐条追加写入 path（中断后可续跑）。"""
    out = []
    with ThreadPoolExecutor(workers) as ex, open(path, "a", encoding="utf-8") as f:
        for r in ex.map(fn, items):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            out.append(r)
    return out


def export_manual_check(per_score: int = 10, seed: int = SEED) -> str:
    """从 LLM 判定中按分数 2 / 1 / 0 各抽 per_score 条，导出供作者人工复核的 CSV（human_score 列留空）。"""
    import csv
    chunks, _ = get_index()
    queries = _cached_jsonl(os.path.join(OUT, "queries.jsonl"), lambda r: r["qid"])
    judged = list(_cached_jsonl(os.path.join(OUT, "judgments.jsonl"), lambda r: (r["qid"], r["chunk"])).values())
    rng = random.Random(seed)
    picked = []
    for s in (2, 1, 0):
        pool = [r for r in judged if r["score"] == s and r["qid"] in queries]
        picked += rng.sample(pool, min(per_score, len(pool)))
    rng.shuffle(picked)                       # 打乱顺序，复核时看不出 LLM 给的分数档
    path = os.path.join(OUT, "manual_check.csv")            # 给复核人：不含 LLM 分数（盲评）
    with open(path, "w", encoding="utf-8-sig", newline="") as f, \
            open(os.path.join(OUT, "manual_check_key.csv"), "w", encoding="utf-8-sig", newline="") as fk:
        w, wk = csv.writer(f), csv.writer(fk)
        w.writerow(["no", "category", "error_feedback", "doc_title", "doc_text", "human_score (0/1/2)"])
        wk.writerow(["no", "qid", "chunk", "llm_score"])
        for n, r in enumerate(picked, 1):
            q = queries[r["qid"]]
            w.writerow([n, q["category"], q["feedback"][:1500], r["title"], chunks[r["chunk"]]["text"][:1500], ""])
            wk.writerow([n, r["qid"], r["chunk"], r["score"]])
    return path


def main():
    from llm import chat
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-cat", type=int, default=30)
    ap.add_argument("-j", type=int, default=8)
    ap.add_argument("--export-check", action="store_true", help="只导出人工复核表 manual_check.csv（各分数档 10 条）")
    args = ap.parse_args()
    if args.export_check:
        print(f"→ {export_manual_check()}")
        return
    os.makedirs(OUT, exist_ok=True)
    queries = sample_queries(load_pool(), args.per_cat)
    by_qid = {q["qid"]: q for q in queries}

    rw_path, jd_path = os.path.join(OUT, "rewrites.jsonl"), os.path.join(OUT, "judgments.jsonl")
    rewrites = {k: r["query"] for k, r in _cached_jsonl(rw_path, lambda r: r["qid"]).items()}

    def rewrite(q):
        text, _ = chat([{"role": "user", "content": REWRITE_PROMPT.format(feedback=q["feedback"][:1500])}],
                       model=REWRITER, temperature=0.0)
        lines = [s for s in text.strip().splitlines() if s.strip()]
        return {"qid": q["qid"], "query": lines[0][:200] if lines else build_query(q["feedback"])}

    for r in _parallel_append(rewrite, [q for q in queries if q["qid"] not in rewrites], rw_path, args.j):
        rewrites[r["qid"]] = r["query"]

    dense = Dense(os.path.join(OUT, "cache"))
    results = {q["qid"]: run_retrievers(q, dense, rewrites[q["qid"]]) for q in queries}

    chunks, _ = get_index()
    judged = _cached_jsonl(jd_path, lambda r: (r["qid"], r["chunk"]))

    def judge(pair):
        qid, i = pair
        text, _ = chat([{"role": "user", "content": JUDGE_PROMPT.format(
            feedback=by_qid[qid]["feedback"][:1500], title=chunks[i]["title"], text=chunks[i]["text"][:1500])}],
            model=JUDGE, temperature=0.0)
        return {"qid": qid, "chunk": i, "title": chunks[i]["title"], "score": parse_score(text), "raw": text[:50]}

    pairs = sorted({(qid, i) for qid, res in results.items() for ids in res.values() for i in ids} - set(judged))
    for r in _parallel_append(judge, pairs, jd_path, args.j):
        judged[(r["qid"], r["chunk"])] = r

    per_query = []
    for q in queries:
        scores = {i: judged[(q["qid"], i)]["score"] or 0 for ids in results[q["qid"]].values() for i in ids}
        per_query.append({"qid": q["qid"], "category": q["category"], "metrics": metrics(results[q["qid"]], scores)})
    summary = summarize(per_query)
    with open(os.path.join(OUT, "queries.jsonl"), "w", encoding="utf-8") as f:
        for q in queries:
            f.write(json.dumps({**q, "rewritten": rewrites[q["qid"]],
                                "results": {n: [chunks[i]["title"] for i in ids]
                                            for n, ids in results[q["qid"]].items()}}, ensure_ascii=False) + "\n")
    with open(os.path.join(OUT, "report.json"), "w", encoding="utf-8") as f:
        json.dump({"config": {"per_cat": args.per_cat, "seed": SEED, "k": K, "rewriter": REWRITER, "judge": JUDGE,
                              "embed": EMBED_MODEL, "rerank": RERANK_MODEL}, "summary": summary}, f, indent=1)
    write_report(summary, args.per_cat)


def write_report(summary: dict, per_cat: int) -> None:
    L = ["# 检索方案离线评估（自动生成）", "",
         f"数据：第 2 阶段修复反馈，按报错类别各抽 {per_cat} 条（种子 {SEED}）；判定模型 {JUDGE}；改写模型 {REWRITER}。",
         "hit@3 = top-3 中至少一个片段含修复所需写法（2 分）；any@3 = 至少一个相关（≥1 分）；"
         "nDCG@3 以该题全部被判定片段为理想排序。数值为百分比。", ""]
    for g, s in summary.items():
        L += [f"## {g}（{s['n']} 条）", "", "| 检索器 | hit@3 | any@3 | nDCG@3 |", "|---|---|---|---|"]
        L += [f"| {n} | {s[n]['hit']} | {s[n]['any']} | {s[n]['ndcg']} |" for n in RETRIEVERS]
        L.append("")
    with open(os.path.join(OUT, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
