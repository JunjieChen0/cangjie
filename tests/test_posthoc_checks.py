import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import posthoc_checks as P  # noqa: E402
import retrieval_eval as RE  # noqa: E402
import review_stats as R  # noqa: E402

IDS = ("1", "2", "3", "4")


def _group(passing: set[str], r0_rate: float) -> dict:
    return {1: {"curve": [r0_rate, 0.0], "passed": {i: i in passing for i in IDS}}}


def _toy_groups() -> tuple[dict, dict]:
    """题 1 在 syntax 第 0 轮已通过（天花板）：全部题上交互 = +25，去掉后为 0。"""
    groups = {("m", "ce", "direct", "hint"): _group({"1", "2"}, 0.0),
              ("m", "ce", "direct", "raw"): _group(set(), 0.0),
              ("m", "ce", "syntax", "hint"): _group({"1", "2"}, 25.0),
              ("m", "ce", "syntax", "raw"): _group({"1"}, 25.0)}
    r0 = {("m", "ce", "direct"): frozenset(), ("m", "ce", "syntax"): frozenset({"1"})}
    return groups, r0


def test_ceiling_groups_keep_only_tasks_failing_round0_in_both_starts():
    groups, r0 = _toy_groups()
    out = P.ceiling_groups(groups, r0)
    assert set(out) == set(groups)
    assert all(set(rep["passed"]) == {"2", "3", "4"} for g in out.values() for rep in g.values())
    assert set(groups[("m", "ce", "direct", "hint")][1]["passed"]) == set(IDS)      # 不改动输入


def test_ceiling_check_removes_interaction_driven_by_round0_passes():
    groups, r0 = _toy_groups()
    assert R.interaction(groups)[0]["interaction"] == 25.0
    row = R.interaction(P.ceiling_groups(groups, r0))[0]
    assert row["n"] == 3 and row["interaction"] == 0.0 and row["p"] == 1.0


def test_ceiling_groups_skip_cells_without_round0_file():
    groups, r0 = _toy_groups()
    del r0[("m", "ce", "syntax")]
    assert P.ceiling_groups(groups, r0) == {}


def _reader(groups: dict, r0_by_key: dict):
    """假的逐题记录：r0_by_key[(模型, 数据集, 起点, 反馈)] 中的题第 0 轮通过（rounds_used = 0）。"""
    def read(key, rep):
        ok = r0_by_key.get(key, set())
        return {i: {"passed": i in ok or v, "rounds_used": 0 if i in ok else 1}
                for i, v in groups[key][rep]["passed"].items()}
    return read


def test_run_r0_unions_round0_passes_over_arms_and_reps():
    groups, _ = _toy_groups()
    read = _reader(groups, {("m", "ce", "syntax", "hint"): {"1"}, ("m", "ce", "syntax", "raw"): {"1"}})
    assert P.run_r0(groups, read) == {("m", "ce", "direct"): [frozenset()] * 2,
                                      ("m", "ce", "syntax"): [frozenset({"1"})] * 2}


def test_run_r0_rejects_records_that_do_not_match_summary_curve():
    groups, _ = _toy_groups()
    read = _reader(groups, {("m", "ce", "syntax", "hint"): {"1"}})      # raw 组的记录给出 R0 = 0，summary 为 25
    with pytest.raises(ValueError):
        P.run_r0(groups, read)


def test_merge_r0_takes_union_and_counts_tasks_without_unanimous_verdict():
    # 题 1：文件与两次运行都通过（一致）；题 2：文件通过、一次运行未通过；题 3：只有一次运行通过
    merged, differ = P.merge_r0({("m", "ce", "direct"): frozenset({"1", "2"})},
                                {("m", "ce", "direct"): [frozenset({"1", "2", "3"}), frozenset({"1"})],
                                 ("m", "ce", "syntax"): [frozenset()]})
    assert merged == {("m", "ce", "direct"): frozenset({"1", "2", "3"}), ("m", "ce", "syntax"): frozenset()}
    assert differ == {("m", "ce", "direct"): 2, ("m", "ce", "syntax"): 0}


def _q(qid: str, hit: dict[str, int], ndcg: dict[str, float] | None = None) -> dict:
    ndcg = ndcg or {}
    return {"qid": qid, "category": "c",
            "metrics": {n: {"hit": hit.get(n, 0), "any": 0, "ndcg": ndcg.get(n, 0.0)} for n in RE.RETRIEVERS}}


def test_select_prefers_hit_then_ndcg():
    rows = [_q("a", {"dense": 1, "hybrid": 1}, {"dense": 0.2, "hybrid": 0.9}), _q("b", {"bm25": 1})]
    assert P.select(rows) == "hybrid"


def test_halves_are_disjoint_cover_all_and_are_deterministic():
    qids = [str(i) for i in range(11)]
    a, b = P.halves(qids, 0)
    assert set(a) | set(b) == set(qids) and not set(a) & set(b) and len(a) == 5
    assert P.halves(list(reversed(qids)), 0) == (a, b)


def test_split_half_selects_on_one_half_and_reports_on_the_other():
    rows = [_q(str(i), {"hybrid": 1}) for i in range(10)]
    res = P.split_half(rows, 0)
    assert [r["direction"] for r in res] == ["A→B", "B→A"]
    for r in res:
        assert r["selected"] == "hybrid" and r["n_test"] == 5
        assert r["hit_selected"] == 100.0 and r["hit_baseline"] == 0.0 and r["hit_diff"] == 100.0


def test_repeated_splits_count_selections_over_both_directions():
    rows = [_q(str(i), {"hybrid": 1}) for i in range(10)]
    res = P.repeated_splits(rows, n=20)
    assert res["n_evaluations"] == 40 and res["selected"] == {"hybrid": 40}
    assert res["share_hit_gain_positive"] == 100.0


def test_retrieval_reconstruction_reproduces_frozen_report():
    rows = P.load_retrieval()
    with open(os.path.join(P.EVAL, "report.json"), encoding="utf-8") as f:
        assert RE.summarize(rows) == json.load(f)["summary"]


def test_family_table_counts_significance_under_each_partition():
    comps = [{"family": "G", "p": 0.03, "p_holm": 0.03, "p_holm_all": 0.06},
             {"family": "A", "p": 0.04, "p_holm": 0.04, "p_holm_all": 0.06}]
    inter = [{"family": "I", "p": 0.001, "p_holm": 0.001}]
    rows = {r["family"]: r for r in P.family_table(comps, inter)}
    # 全部合并 Holm：0.001×3、0.03×2、0.04×1 → 0.003、0.06、0.06
    assert rows["G"] == {"family": "G", "n": 1, "sig_within": 1, "sig_gar": 0, "sig_all": 0}
    assert rows["A"]["sig_all"] == 0
    assert rows["I"]["sig_gar"] is None and rows["I"]["sig_all"] == 1


def test_heldout_hint_lists_only_hint_vs_raw_outside_humaneval_and_family_g_of_review():
    row = {"model": "m", "prompt": "direct", "a": "hint", "b": "raw", "n": 84, "diff": 5.0,
           "ci_lo": 1.0, "ci_hi": 9.0, "p_holm": 0.01}
    stats = {"stage3": {"comparisons": [dict(row, ds="ce"), dict(row, ds="he"), dict(row, ds="ce", a="rag")]},
             "review": {"comparisons": [dict(row, ds="or", family="G"), dict(row, ds="ce", family="A")]}}
    out = P.heldout_hint(stats)
    assert [(r["source"], r["ds"]) for r in out] == [("stage3", "ce"), ("review", "or")]
