import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import stage3_stats as S  # noqa: E402


def _write_group(base, name, passed: dict, n=None, errors=0, curve=None, tokens=(1000, 2000), err=None):
    """err: {题号: 报错文本}，这些题写成出错行（passed=False）。"""
    runs = os.path.join(base, "runs")
    os.makedirs(runs, exist_ok=True)
    err = err or {}
    errors = errors or len(err)
    with open(os.path.join(runs, name + ".jsonl"), "w", encoding="utf-8") as f:
        for i, ok in passed.items():
            row = {"id": i, "passed": ok} if i not in err else {"id": i, "passed": False, "error": err[i]}
            f.write(json.dumps(row) + "\n")
    s = {"n": len(passed) if n is None else n, "errors": errors,
         "pass@1_by_round": curve or [0.0, 100 * sum(passed.values()) / len(passed)],
         "total_prompt_tokens": tokens[0], "total_completion_tokens": tokens[1]}
    with open(os.path.join(runs, name + ".summary.json"), "w", encoding="utf-8") as f:
        json.dump(s, f)


def test_parse_name_handles_compile_only_and_reps():
    assert S.parse_name("doubao_mini_he_direct_hint_co_rep2") == ("doubao_mini", "he", "direct", "hint_co", 2)
    assert S.parse_name("ds_v41f_ce_syntax_rag_rep1") == ("ds_v41f", "ce", "syntax", "rag", 1)
    assert S.parse_name("kimik31p_or_direct_raw_rep3") == ("kimik31p", "or", "direct", "raw", 3)
    assert S.parse_name("not_a_group") is None


def test_load_groups_skips_incomplete_or_errored(tmp_path):
    ok = {i: True for i in range(4)}
    _write_group(tmp_path, "doubao_mini_or_direct_raw_rep1", ok)
    _write_group(tmp_path, "doubao_mini_or_direct_raw_rep2", ok, errors=1)
    _write_group(tmp_path, "doubao_mini_or_direct_hint_rep1", {0: True, 1: False})   # n=2 ≠ 4
    g = S.load_groups(str(tmp_path), {"or": 4})
    assert list(g) == [("doubao_mini", "or", "direct", "raw")]
    assert list(g[("doubao_mini", "or", "direct", "raw")]) == [1]


def test_kimi_timeouts_count_as_fail_other_models_stay_strict(tmp_path):
    ok = {i: True for i in range(4)}
    timeout = "APITimeoutError('Request timed out.')"
    _write_group(tmp_path, "kimik31p_ce_direct_raw_rep1", ok, err={1: timeout})
    _write_group(tmp_path, "kimik31p_ce_direct_hint_rep1", ok, err={2: "RuntimeError('boom')"})
    _write_group(tmp_path, "ds_v41f_ce_direct_raw_rep1", ok, err={1: timeout})
    g = S.load_groups(str(tmp_path), {"ce": 4})
    assert list(g) == [("kimik31p", "ce", "direct", "raw")]     # Kimi 非超时错误、DeepSeek 超时都跳过
    rep = g[("kimik31p", "ce", "direct", "raw")][1]
    assert rep["timeouts"] == 1 and rep["passed"]["1"] is False and sum(rep["passed"].values()) == 3
    row, = S.summarize(g)
    assert row["timeouts"] == 1
    assert "API 超时按未通过计入分母" in S.write_markdown([row], [], "t")
    assert S.load_groups(str(tmp_path), {"ce": 4}, timeout_as_fail=frozenset()) == {}   # 全部严格


def test_sensitivity_drops_problems_timed_out_in_either_arm(tmp_path):
    timeout = "APITimeoutError('Request timed out.')"
    ok = {i: True for i in range(4)}
    _write_group(tmp_path, "kimik31p_ce_direct_raw_rep1", ok, err={1: timeout, 2: timeout})
    _write_group(tmp_path, "kimik31p_ce_direct_hint_rep1", ok, err={3: timeout})
    groups = S.load_groups(str(tmp_path), {"ce": 4})
    main, = S.compare(groups)
    sens, = S.compare(groups, drop_timeouts=True)
    assert (main["n"], main["diff"]) == (4, 25.0)       # hint − raw 按题：0, +1, +1, −1 → 平均 +25
    assert (sens["n"], sens["diff"]) == (1, 0.0)        # 去掉 1、2、3 后只剩第 0 题


def test_kimi_timeout_group_skipped_while_rerun_in_progress(tmp_path):
    _write_group(tmp_path, "kimik31p_ce_direct_raw_rep1", {i: True for i in range(4)},
                 err={1: "APITimeoutError('Request timed out.')"})
    with open(tmp_path / "runs" / "kimik31p_ce_direct_raw_rep1.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"id": 1, "passed": True}) + "\n")               # 补跑追加的行，summary 仍是旧的
    assert S.load_groups(str(tmp_path), {"ce": 4}) == {}


def test_per_problem_diff_averages_over_reps():
    a = {1: {"passed": {"0": True, "1": True}}, 2: {"passed": {"0": True, "1": False}}}
    b = {1: {"passed": {"0": False, "1": True}}, 2: {"passed": {"0": False, "1": True}}}
    assert sorted(S.per_problem_diff(a, b)) == [-0.5, 1.0]


def test_sign_flip_p_extremes():
    assert S.sign_flip_p([0.0] * 20) == 1.0
    assert S.sign_flip_p([1.0] * 20) < 0.001
    assert S.sign_flip_p([1.0, -1.0] * 10) > 0.9


def test_compare_applies_holm_over_family(tmp_path):
    n = 30
    for r in (1, 2, 3):
        _write_group(tmp_path, f"doubao_mini_or_direct_raw_rep{r}", {i: i < 5 for i in range(n)})
        _write_group(tmp_path, f"doubao_mini_or_direct_hint_rep{r}", {i: i < 25 for i in range(n)})
        _write_group(tmp_path, f"doubao_mini_or_direct_blind_rep{r}", {i: i < 4 for i in range(n)})
    rows = S.compare(S.load_groups(str(tmp_path), {"or": n}))
    by = {(r["a"], r["b"]): r for r in rows}
    assert set(by) == {("hint", "raw"), ("raw", "blind")}
    hr = by[("hint", "raw")]
    assert abs(hr["diff"] - 66.67) < 0.01 and hr["ci_lo"] > 0 and hr["p"] < 0.001
    assert hr["p_holm"] >= hr["p"] and by[("raw", "blind")]["p_holm"] >= by[("raw", "blind")]["p"]
    assert len(hr["mcnemar_per_rep"]) == 3


def test_compare_excludes_flaky_problems_in_sensitivity(tmp_path):
    for r in (1, 2, 3):
        _write_group(tmp_path, f"doubao_mini_he_direct_raw_rep{r}", {i: False for i in range(4)})
        _write_group(tmp_path, f"doubao_mini_he_direct_hint_rep{r}", {i: i == 0 for i in range(4)})
    groups = S.load_groups(str(tmp_path), {"he": 4})
    full, = S.compare(groups)
    excl, = S.compare(groups, {"he": frozenset({"0"})})
    assert (full["n"], full["diff"]) == (4, 25.0)
    assert (excl["n"], excl["diff"]) == (3, 0.0)
    assert S.FLAKY == {"he": frozenset({"20"}), "ce": frozenset({"58"})}


def test_summarize_reports_mean_sd_and_cost(tmp_path):
    for r, k in ((1, 2), (2, 3), (3, 4)):
        _write_group(tmp_path, f"doubao_mini_or_direct_raw_rep{r}", {i: i < k for i in range(10)},
                     tokens=(1_000_000, 1_000_000))
    row = S.summarize(S.load_groups(str(tmp_path), {"or": 10}))[0]
    assert (row["r5_mean"], round(row["r5_sd"], 2), row["reps"]) == (30.0, 10.0, 3)
    assert abs(row["yuan_per_pass"] - 3 * 2.2 / 9) < 1e-6          # doubao 0.2+2.0 元/百万，共 9 次通过
