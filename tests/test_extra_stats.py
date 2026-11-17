import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from extra_stats import bootstrap_ci, calls_until, cost_yuan, holm, pass_at_k  # noqa: E402


def test_holm_matches_textbook_example():
    # p = [0.01, 0.04, 0.03] → 排序后乘以 3,2,1 → [0.03, 0.06, 0.06]（单调化）
    assert holm([0.01, 0.04, 0.03]) == [0.03, 0.06, 0.06]


def test_holm_keeps_input_order():
    adj = holm([0.9, 0.001])
    assert adj == [0.9, 0.002]   # 最大的 p 乘以 1


def test_holm_caps_at_one():
    assert holm([0.6, 0.6]) == [1.0, 1.0]


def test_pass_at_k_edges():
    assert pass_at_k(6, 0, 3) == 0.0
    assert pass_at_k(6, 6, 1) == 1.0
    assert abs(pass_at_k(6, 1, 1) - 1 / 6) < 1e-12
    assert pass_at_k(6, 4, 3) == 1.0  # 失败样本不足 k 个时必定命中


def test_cost_uses_per_million_prices():
    assert cost_yuan(1_000_000, 1_000_000, "doubao") == {"list": 2.2}
    assert cost_yuan(500_000, 0, "ds_v41f") == {"offpeak": 0.5, "peak": 1.0}


def test_calls_until_counts_generation_plus_repairs():
    row = {"history": [{}, {}, {}]}           # 第 0 轮 + 2 次修复
    assert calls_until(row, 0, False) == 1
    assert calls_until(row, 1, False) == 2
    assert calls_until(row, 5, False) == 3
    assert calls_until(row, 5, True) == 2     # --init 时第 0 轮不调用模型


def test_bootstrap_ci_degenerate_sample():
    mean, lo, hi = bootstrap_ci([1.0] * 10, n_boot=200)
    assert (mean, lo, hi) == (100.0, 100.0, 100.0)
