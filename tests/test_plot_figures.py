import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import plot_figures as F  # noqa: E402


def test_curve_band_mean_and_sd():
    reps = {1: {"curve": [10.0, 20.0]}, 2: {"curve": [10.0, 30.0]}, 3: {"curve": [10.0, 40.0]}}
    mean, sd = F.curve_band(reps)
    assert mean == [10.0, 30.0] and sd == [0.0, 10.0]
    assert F.curve_band({1: {"curve": [5.0, 6.0]}}) == ([5.0, 6.0], [0.0, 0.0])


def test_run_cost_adds_shared_r0_to_mean_repair_cost():
    reps = {1: {"tokens": (1_000_000, 0)}, 2: {"tokens": (3_000_000, 2_000_000)}}
    # doubao 0.2 / 2.0 元每百万：输入 1M(R0) + 平均 2M，输出 0 + 平均 1M
    assert abs(F.run_cost(reps, (1_000_000, 0), "doubao_mini") - (3 * 0.2 + 1 * 2.0)) < 1e-9
    # DeepSeek 取高峰价 2 / 8
    assert abs(F.run_cost({1: {"tokens": (1_000_000, 1_000_000)}}, (0, 0), "ds_v41f") - 10.0) < 1e-9


def test_merge_small_categories_into_other():
    cats = {str(i): "foreign_syntax" for i in range(10)} | {"a": "timeout", "b": "test_failure"}
    out = F.merge_small_categories(cats)
    assert out["0"] == "foreign_syntax" and out["a"] == out["b"] == "other"


def test_error_repair_rates_by_category():
    cats = {"0": "foreign_syntax", "1": "foreign_syntax", "2": "test_failure"}
    reps = {1: {"passed": {"0": True, "1": False, "2": True}}, 2: {"passed": {"0": True, "1": True, "2": False}}}
    out = F.error_repair_rates(cats, reps)
    assert out["foreign_syntax"][:2] == (2, 75.0)
    assert out["test_failure"][:2] == (1, 50.0)
