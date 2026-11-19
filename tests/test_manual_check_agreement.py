import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import manual_check_agreement as M  # noqa: E402


def test_perfect_agreement():
    a = [0, 1, 2, 0, 1, 2]
    r = M.agreement(a, a)
    assert r["exact"] == 6 and r["kappa"] == 1.0 and r["quadratic_kappa"] == 1.0 and r["spearman"] == 1.0
    assert r["disagreements"] == []


def test_kappa_matches_hand_computation():
    h, m = [0, 0, 1, 1], [0, 1, 1, 1]
    # 观察一致 3/4；期望一致 = (2*1 + 2*3)/16 = 0.5 → κ = (0.75-0.5)/0.5 = 0.5
    assert abs(M.kappa(h, m) - 0.5) < 1e-9
    r = M.agreement(h, m)
    assert r["llm_higher"] == 1 and r["human_higher"] == 0
    assert r["disagreements"] == [{"no": 2, "human": 0, "llm": 1}]
    assert r["binary_ge1"] == {"agree": 3, "human_pos": 2, "llm_pos": 3}


def test_spearman_uses_average_ranks_for_ties():
    assert M._ranks([2, 0, 2, 1]) == [3.5, 1.0, 3.5, 2.0]
    assert abs(M.spearman([0, 1, 2], [2, 1, 0]) + 1) < 1e-9
