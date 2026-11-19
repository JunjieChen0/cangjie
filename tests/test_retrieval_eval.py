import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import retrieval_eval as R  # noqa: E402


def test_rrf_rewards_documents_ranked_high_by_both():
    assert R.rrf([[1, 2, 3], [3, 1, 4]])[:2] == [1, 3]
    assert R.rrf([[5], [6]]) == [5, 6]                      # 同分按首次出现顺序


def test_metrics_hit_any_and_ndcg():
    judged = {1: 2, 2: 1, 3: 0, 4: 0}
    m = R.metrics({"a": [1, 2, 3], "b": [3, 4, 2], "c": []}, judged)
    assert (m["a"]["hit"], m["a"]["any"], round(m["a"]["ndcg"], 6)) == (1, 1, 1.0)
    assert (m["b"]["hit"], m["b"]["any"]) == (0, 1) and 0 < m["b"]["ndcg"] < 1
    assert m["c"] == {"hit": 0, "any": 0, "ndcg": 0.0}


def test_parse_score_takes_first_digit_in_range():
    assert R.parse_score("2") == 2 and R.parse_score("Score: 1.") == 1 and R.parse_score("n/a") is None


def test_pool_dedupes_skips_last_round_and_samples_by_category(tmp_path):
    rows = [{"id": 1, "history": [{"failure_kind": "compile_error", "feedback": "error: undeclared identifier 'abs'"},
                                  {"failure_kind": "compile_error", "feedback": "error: expected ')' found 'x'"},
                                  {"failure_kind": "passed", "feedback": ""}]},
            {"id": 2, "history": [{"failure_kind": "compile_error", "feedback": "error: undeclared identifier 'abs'"},
                                  {"failure_kind": "test_failure", "feedback": "1 of 2 tests failed."}]}]
    p = tmp_path / "x.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    pool = R.load_pool([str(p)])
    assert sorted(it["category"] for it in pool) == ["api_or_undeclared", "foreign_syntax"]
    qs = R.sample_queries(pool, per_cat=5)
    assert len({q["qid"] for q in qs}) == 2 and qs[0]["category"] == "foreign_syntax"
    assert R.sample_queries(pool, per_cat=1)[0]["qid"] == qs[0]["qid"]          # 同一条报错同一个 qid


def test_summarize_reports_percentages_per_category():
    m = {n: {"hit": 1, "any": 1, "ndcg": 0.5} for n in R.RETRIEVERS}
    s = R.summarize([{"category": "foreign_syntax", "metrics": m}])
    assert s["all"]["n"] == 1 and s["all"]["bm25"] == {"hit": 100.0, "any": 100.0, "ndcg": 50.0}
    assert s["api_or_undeclared"]["n"] == 0
