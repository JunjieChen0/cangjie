import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import robustness_checks as RC  # noqa: E402
import stage3_stats as S  # noqa: E402


def test_no_difference_gives_p_one():
    assert RC.sign_flip_p_hi([0.0, 0.0, 0.0]) == 1.0


def test_matches_exact_two_sided_p_for_all_positive_diffs():
    # 10 道题差值都为 +1：精确双侧 p = 2 / 2^10 ≈ 0.00195
    p = RC.sign_flip_p_hi([1.0] * 10, n_perm=100_000)
    assert abs(p - 2 / 1024) < 0.0005


def test_is_deterministic_and_agrees_with_main_test():
    diffs = [1 / 3, 2 / 3, -1 / 3, 1.0, 0.0, 1 / 3, 1 / 2, -1 / 6] * 5
    assert RC.sign_flip_p_hi(diffs, n_perm=20_000) == RC.sign_flip_p_hi(diffs, n_perm=20_000)
    assert abs(RC.sign_flip_p_hi(diffs, n_perm=20_000) - S.sign_flip_p(diffs, n_perm=20_000)) < 0.02


def test_rejects_diffs_that_cannot_be_scaled_exactly():
    with pytest.raises(ValueError):
        RC.sign_flip_p_hi([1 / 7, 0.5])


def test_defective_tasks_extend_flaky_with_benchmark_defects():
    assert RC.DEFECTIVE["he"] == S.FLAKY["he"]
    assert RC.DEFECTIVE["ce"] == S.FLAKY["ce"] | {"48", "53"}


def test_permutation_test_context_restores_original_function():
    before = S.sign_flip_p
    with RC.permutation_test(RC.sign_flip_p_hi):
        assert S.sign_flip_p is RC.sign_flip_p_hi
    assert S.sign_flip_p is before


def test_contrast_reports_significance_flips_and_sign_changes():
    row = {"family": "A", "model": "m", "ds": "ce", "prompt": "direct", "a": "x", "b": "y", "n": 84}
    main = [row | {"diff": 8.0, "p_holm": 0.03}, row | {"b": "z", "diff": 1.0, "p_holm": 1.0}]
    alt = [row | {"diff": 7.5, "p_holm": 0.06, "n": 80}, row | {"b": "z", "diff": -0.5, "p_holm": 1.0, "n": 80}]
    c = RC.contrast(main, alt)
    assert c["significant_main"] == {"A": 1} and c["significant_alt"] == {}
    assert [x["b"] for x in c["changed"]] == ["y", "z"] and c["max_abs_diff_shift"] == 1.5
