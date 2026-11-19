import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import case_examples as C  # noqa: E402

SYNTAX = "error: expected '(' after 'if', found 'x'"
API = "error: 'append' is not a member of class 'ArrayList<Int64>'"


def _row(passed, fb, codes=("a\nb", "a\nc")):
    return {"passed": passed, "history": [{"failure_kind": "compile_error", "feedback": fb, "code": codes[0]},
                                          {"failure_kind": "passed" if passed else "compile_error", "code": codes[1]}]}


def test_pick_requires_raw_all_fail_arm_all_pass_and_category():
    raw = [{"1": _row(False, SYNTAX), "2": _row(False, API), "3": _row(False, SYNTAX)} for _ in range(3)]
    raw[2]["3"] = _row(True, SYNTAX)                                   # 第 3 题 raw 有一次通过，排除
    arm = [{"1": _row(True, SYNTAX), "2": _row(True, API), "3": _row(True, SYNTAX)} for _ in range(3)]
    i, diff = C.pick(raw, arm, "foreign_syntax")
    assert i == "1" and "-b" in diff and "+c" in diff
    assert C.pick(raw, arm, "api_or_undeclared")[0] == "2"
    assert C.pick(raw, arm, "type_or_mutability") is None


def test_specific_hint_filter_and_path_stripping():
    assert C.has_specific_hint(SYNTAX)
    assert not C.has_specific_hint("error: something unusual happened")
    text = "Exception: Test failed!\n\t at default.test_a()(C:\\Users\\x\\AppData\\Local\\Temp\\cj_1\\main.cj:3)"
    assert C.strip_paths(text) == "Exception: Test failed!\n\t at default.test_a()"
