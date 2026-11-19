import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import check_numbers as C  # noqa: E402

STATS = {
    "summary": [{"r0": 10.98, "r5_mean": 51.63, "r5_sd": 1.86, "curve_mean": [10.98, 51.63]}],
    "comparisons": [{"diff": -2.03, "ci_lo": -7.11, "ci_hi": 3.05, "p": 0.485, "p_holm": 1.0,
                     "mcnemar_per_rep": [0.7266]}],
    "sensitivity_excl_flaky": [{"diff": 0.0, "ci_lo": 0.0, "ci_hi": 0.0, "p": 1.0, "p_holm": 0.0208,
                                "mcnemar_per_rep": []}],
}


def test_matching_numbers_pass_in_any_minus_and_percent_style():
    known = C.known_values([STATS])
    text = "差值 −2.03 [−7.11, +3.05]，p = 0.4850，p(Holm) 0.0208；R5 51.63% ± 1.86%，R0 10.98%"
    assert C.check_text(text, known) == []


def test_unknown_numbers_reported_with_line_number():
    known = C.known_values([STATS])
    text = "第一行 +2.03 正确符号错\n第二行 51.63 ± 1.87\n第三行 p = 0.4851，<0.0001 不检查"
    assert C.check_text(text, known) == [(1, "+2.03"), (2, "51.63 ± 1.87"), (3, "0.4851")]
