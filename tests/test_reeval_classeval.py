import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from reeval_classeval import round_curves  # noqa: E402


def test_passed_at_round0_counts_from_round0():
    rows = [{"rounds_used": 0, "passed_main": True, "passed_all": True}]
    main, all_ = round_curves(rows, max_round=2)
    assert main == [100.0, 100.0, 100.0]
    assert all_ == [100.0, 100.0, 100.0]


def test_repaired_at_round2_counts_from_round2():
    rows = [{"rounds_used": 2, "passed_main": True, "passed_all": True}]
    main, all_ = round_curves(rows, max_round=3)
    assert main == [0.0, 0.0, 100.0, 100.0]
    assert all_ == [0.0, 0.0, 100.0, 100.0]


def test_main_only_pass_is_not_counted_in_all_tests_curve():
    rows = [{"rounds_used": 1, "passed_main": True, "passed_all": False}]
    main, all_ = round_curves(rows, max_round=1)
    assert main == [0.0, 100.0]
    assert all_ == [0.0, 0.0]


def test_failed_row_never_counts_and_percent_uses_all_rows():
    rows = [
        {"rounds_used": 5, "passed_main": False, "passed_all": False},
        {"rounds_used": 0, "passed_main": True, "passed_all": True},
    ]
    main, all_ = round_curves(rows, max_round=1)
    assert main == [50.0, 50.0]
    assert all_ == [50.0, 50.0]
