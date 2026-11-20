import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import sensitivity_report as S  # noqa: E402


def _c(diff, p, n=10):
    return {"model": "m", "ds": "he", "prompt": "direct", "a": "hint", "b": "raw", "diff": diff, "p_holm": p, "n": n}


def test_flags_significance_or_sign_change_only():
    comps = [_c(10, 0.01), _c(5, 0.20), _c(3, 0.30), _c(8, 0.01)]
    sens = [_c(9, 0.02, 9), _c(6, 0.04, 9), _c(-1, 0.90, 9), _c(7, 0.20, 9)]
    changed = S.flips(comps, sens)
    assert [(c["diff_all"], c["diff_after"]) for c in changed] == [(5, 6), (3, -1), (8, 7)]
    sec = S.section({"comparisons": comps, "sensitivity_excl_flaky": sens,
                     "summary": [{"model": "kimik31p", "ds": "ce", "prompt": "direct", "feedback": "raw",
                                  "reps": 3, "timeouts": 2}]})
    assert (sec["significant_all"], sec["significant_after"], sec["max_abs_diff_shift"]) == (2, 2, 4)
    assert sec["timeouts"][0]["timeouts"] == 2
