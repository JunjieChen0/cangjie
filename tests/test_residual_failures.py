import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import residual_failures as R  # noqa: E402
from runner import RunResult  # noqa: E402


def _row(i, passed, kinds=("compile_error",), status="[True, False]", fb="x", error=None):
    hist = [{"round": k, "failure_kind": kind, "feedback": fb, "code": f"c{k}", "status": status}
            for k, kind in enumerate(kinds)]
    row = {"id": i, "passed": passed, "history": hist}
    if error:
        row["error"] = error
    return row


def test_last_failure_and_near_miss():
    assert R.last_failure(_row(1, False, error="APITimeoutError")) == "api_timeout"
    assert R.last_failure(_row(1, False, kinds=("compile_error", "test_failure"))) == "test_failure"
    assert R.is_near_miss("[True, True, False]") and not R.is_near_miss("[True, False, False]")
    assert not R.is_near_miss("") and not R.is_near_miss("[]")
    assert R.is_near_miss([True, False]) and not R.is_near_miss([])          # 日志里实际是 JSON 列表


def test_hard_problems_take_details_from_first_non_timeout_record():
    t = _row(5, False, error="APITimeoutError")
    t["history"] = []
    ok = _row(5, False, kinds=("test_failure",), status=[True, False],
              fb=r"Test failed! at default.test_a()(C:\Users\x\AppData\Local\Temp\cj_1\main.cj:3)")
    ok["history"][-1]["code"] = "class Foo {}"
    runs = {("m", "direct", "raw"): [{"5": t}], ("m", "direct", "hint"): [{"5": ok}]}
    row, = R.hard_problems(runs, "m")
    assert row["class"] == "Foo" and row["status"] == [True, False]
    assert row["kinds"] == ["api_timeout", "test_failure"]
    assert "Users" not in row["feedback_head"] and "test_a()" in row["feedback_head"]   # 去掉本机路径


def test_residual_summary_counts_failures_near_misses_and_always_failing():
    rep1 = {"1": _row(1, False, kinds=("test_failure",), status="[True, False]"),
            "2": _row(2, False, kinds=("test_failure",), status="[False, False]"),
            "3": _row(3, True)}
    rep2 = {"1": _row(1, False, kinds=("test_failure",), status="[True, False]"),
            "2": _row(2, True), "3": _row(3, False, error="APITimeoutError")}
    s = R.residual_summary([rep1, rep2])
    assert s["fail"] == 4 and s["cats"] == {"test_failure": 3, "api_timeout": 1}
    assert (s["test_fail"], s["near_miss"]) == (3, 2)
    assert s["always"] == ["1"]


def test_truncation_census_only_counts_feedback_shown_to_model():
    long, short = "y" * R.STORED_CAP, "y" * 10
    rows = [_row(1, False, kinds=("compile_error", "test_failure", "test_failure"), fb=long),
            _row(2, False, kinds=("test_failure", "test_failure"), fb=short)]
    c = R.truncation_census(rows)
    # 每题最后一条是最终代码的评测，不算；第 1 题前两条（存满）、第 2 题第一条（未满）
    assert c == {("compile_error", True): 1, ("test_failure", True): 1, ("test_failure", False): 1}


def test_error_line_retention_counts_error_lines_kept_before_cap():
    text = "error: a\n  ==> x\n" + "y" * 20 + "\nerror: b\nerror: c\n"
    total, kept = R.error_line_retention(text, cap=len("error: a\n  ==> x\n") + 30)   # 截到 "error: b" 之后
    assert (total, kept) == (3, 2)
    assert R.error_line_retention(text, cap=len("error: a\n  ==> x\n") + 25) == (3, 1)   # "error: b" 被截成 "erro"
    assert R.error_line_retention("1 of 2 tests failed.", cap=5) == (0, 0)


def test_full_feedback_text_is_uncapped():
    ce = [RunResult(False, "compile_error", compile_stderr="error: x\n" + "e" * 4000)]
    assert R.full_feedback_text(ce).startswith("error: x") and len(R.full_feedback_text(ce)) == 4009


def test_summarize_recheck_weights_duplicates_and_counts_retention():
    long_ce = "error: a\n" + "x" * 3100 + "\nerror: b\n"          # 超过 3000，保留 1/2 条报错行
    lost = "y" * 3100 + "\nerror: c\n"                            # 超过 3000，报错行全部丢失
    items = [("m compile_error", 2, long_ce), ("m compile_error", 1, lost), ("m compile_error", 1, "error: d")]
    s = R.summarize_recheck(items)["m compile_error"]
    assert (s["checked"], s["over_cap"], s["unique_code"]) == (4, 3, 3)
    assert (s["error_lines_total"], s["error_lines_kept"], s["lost_all_errors"]) == (5, 2, 1)
    assert s["length_median"] == (len(lost) + len(long_ce)) / 2          # 按次数加权：短、lost、long、long
    assert s["length_max"] == len(long_ce)


def test_coding_label_uses_csv_and_marks_pure_timeouts(tmp_path):
    p = tmp_path / "coding.csv"
    p.write_text("id,class,category,subtype,evidence,coder,reviewer\n5,Foo,隐含规格,边界或非法输入约定,e,c,\n",
                 encoding="utf-8")
    coding = R.load_coding(str(p))
    assert R.coding_label({"id": "5", "kinds": ["test_failure"]}, coding) == "隐含规格：边界或非法输入约定"
    assert R.coding_label({"id": "5", "kinds": ["api_timeout"]}, coding) == "API 超时（无代码）"
    assert R.coding_label({"id": "9", "kinds": ["test_failure"]}, coding) == ""
    assert R.load_coding(str(tmp_path / "missing.csv")) == {}


def test_full_feedback_length_matches_uncapped_aggregate():
    ok = RunResult(True, "passed")
    bad = RunResult(False, "test_failure", run_stdout="z" * 4000)
    n = R.full_feedback_length([ok, bad])
    assert n == len("1 of 2 tests failed.\n\n") + len("[test #1 test_failure]\n") + 4000
    ce = [RunResult(False, "compile_error", compile_stderr="e" * 3500)] * 2
    assert R.full_feedback_length(ce) == 3500                    # 相同编译错误去重
