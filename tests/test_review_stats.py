import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import review_stats as R  # noqa: E402

N = 6


def _group(base, name, k, history=None):
    """前 k 题通过；history 给出时写进每一行。"""
    runs = os.path.join(base, "runs")
    os.makedirs(runs, exist_ok=True)
    with open(os.path.join(runs, name + ".jsonl"), "w", encoding="utf-8") as f:
        for i in range(N):
            f.write(json.dumps({"id": i, "passed": i < k, "history": history or []}) + "\n")
    with open(os.path.join(runs, name + ".summary.json"), "w", encoding="utf-8") as f:
        json.dump({"n": N, "errors": 0, "pass@1_by_round": [0.0, 100 * k / N],
                   "total_prompt_tokens": 10, "total_completion_tokens": 10}, f)


def _arm(base, stem, k, **kw):
    for r in (1, 2, 3):
        _group(base, f"{stem}_rep{r}", k, **kw)


def test_reuse_rule_pairs_ds_with_stage3_but_never_old_kimi(tmp_path):
    review, stage3 = str(tmp_path / "review"), str(tmp_path / "stage3")
    hist = [{"round": "0", "action": "test"}, {"round": "1", "action": "search"}, {"round": "2", "action": "test"}]
    _arm(review, "ds_v41f_he_direct_agent", 5, history=hist)
    _arm(stage3, "ds_v41f_he_direct_rag", 1)
    _arm(stage3, "kimik31p_he_direct_rag", 1)                  # 旧 Kimi：不得合并
    _arm(review, "kimik31p_he_direct_agent", 5)
    groups = R.load_all(review, [stage3], {"he": N})
    assert ("ds_v41f", "he", "direct", "rag") in groups
    assert ("kimik31p", "he", "direct", "rag") not in groups
    rows = R.run_families(groups)
    assert [(r["family"], r["model"], r["a"], r["b"]) for r in rows] == [("A", "ds_v41f", "agent", "rag")]
    assert rows[0]["diff"] > 0 and "p_holm_all" in rows[0]
    beh, = [b for b in R.agent_behavior(groups, review) if b["model"] == "ds_v41f"]
    assert (beh["problems"], beh["search_per_problem"], beh["pct_any_search"], beh["mean_steps"]) == (18, 1.0, 100.0, 2)


def test_family_g_only_new_models_kimi_and_ds_ce_syntax(tmp_path):
    review = str(tmp_path / "review")
    for stem in ("glm53f_he_direct", "doubao_mini_he_direct", "ds_v41f_ce_syntax"):
        _arm(review, f"{stem}_hint", 4)
        _arm(review, f"{stem}_raw", 2)
    groups = R.load_all(review, [], {"he": N, "ce": N})
    fam_g = {(r["model"], r["ds"]) for r in R.run_families(groups) if r["family"] == "G"}
    assert fam_g == {("glm53f", "he"), ("ds_v41f", "ce")}       # doubao_mini 的 hint vs raw 已在第 3 阶段比较过


def test_interaction_is_hint_gain_direct_minus_syntax(tmp_path):
    review = str(tmp_path / "review")
    for model in ("glm53f", "doubao_mini"):
        _arm(review, f"{model}_he_direct_hint", 4)
        _arm(review, f"{model}_he_direct_raw", 2)
        _arm(review, f"{model}_he_syntax_hint", 3)
        _arm(review, f"{model}_he_syntax_raw", 3)
    rows = {r["model"]: r for r in R.interaction(R.load_all(review, [], {"he": N}))}
    g = rows["glm53f"]
    assert (g["family"], g["n"], g["hint_gain_direct"], g["hint_gain_syntax"]) == ("I", N, 33.33, 0.0)
    assert g["interaction"] == 33.33 and "p_holm" in g
    assert rows["doubao_mini"]["family"] == "I-explore"


def _group_with_errors(base, name, errors):
    """前 N−len(errors) 题通过；后几题各带一个 error（未通过）。"""
    runs = os.path.join(base, "runs")
    os.makedirs(runs, exist_ok=True)
    with open(os.path.join(runs, name + ".jsonl"), "w", encoding="utf-8") as f:
        for i in range(N):
            row = {"id": i, "passed": i < N - len(errors), "history": []}
            if i >= N - len(errors):
                row["error"] = errors[i - (N - len(errors))]
            f.write(json.dumps(row) + "\n")
    with open(os.path.join(runs, name + ".summary.json"), "w", encoding="utf-8") as f:
        json.dump({"n": N, "errors": len(errors), "pass@1_by_round": [0.0, 50.0],
                   "total_prompt_tokens": 10, "total_completion_tokens": 10}, f)


def test_glm_timeouts_count_as_fail_only_in_review(tmp_path):
    review, stage3 = str(tmp_path / "review"), str(tmp_path / "stage3")
    timeout = "APITimeoutError('Request timed out.')"
    _group_with_errors(review, "glm53f_ce_syntax_rag_rep1", [timeout])                      # 只有超时：收进来
    _group_with_errors(review, "glm53f_ce_syntax_hint_rep1", [timeout, "RateLimitError(429)"])  # 有非超时错误：跳过
    _group_with_errors(review, "doubao21l_ce_syntax_rag_rep1", [timeout])                   # 其他模型仍要求 errors = 0
    _group_with_errors(stage3, "ds_v41f_ce_syntax_rag_rep1", [timeout])                     # 第 3 阶段口径不变
    groups = R.load_all(review, [stage3], {"ce": N})
    assert list(groups) == [("glm53f", "ce", "syntax", "rag")]
    rep = groups[("glm53f", "ce", "syntax", "rag")][1]
    assert rep["timeouts"] == 1 and rep["passed"]["5"] is False and sum(rep["passed"].values()) == N - 1
    assert R.REVIEW_TIMEOUT_AS_FAIL == {"kimik31p", "glm53f"}


def test_markdown_lists_each_family():
    res = {"missing": ["u2f_he_direct_rag2（0/3）"], "summary": [], "comparisons": [],
           "sensitivity_excl_flaky": [], "agent_behavior": []}
    md = R.write_markdown(res, pilot=False)
    assert "族 G" in md and "族 A" in md and "族 R" in md and "u2f_he_direct_rag2（0/3）" in md
