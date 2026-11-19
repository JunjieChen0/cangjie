import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import rounds10_stats as T  # noqa: E402


def test_round_gains():
    assert T.round_gains([10.0, 15.0, 22.5]) == [5.0, 7.5]
    assert T.round_gains([10.0]) == []


def test_feedback_rows_report_r5_r10_and_gains():
    def rep(c, tokens=(1_000_000, 0)):
        return {"curve": c, "passed": {"0": True}, "tokens": tokens}
    groups = {("doubao_mini", "he", "direct", "hint"): {
        1: rep([10.0, 20.0, 30.0, 40.0, 50.0, 50.0, 52.0, 54.0, 56.0, 58.0, 60.0]),
        2: rep([10.0, 20.0, 30.0, 40.0, 50.0, 54.0, 56.0, 58.0, 60.0, 62.0, 64.0])}}
    r0 = {("doubao_mini", "he", "direct"): (0, 0)}
    row, = T.feedback_rows(groups, r0)
    assert (row["feedback"], row["reps"]) == ("hint", 2)
    assert (row["r5_mean"], row["r10_mean"]) == (52.0, 62.0)
    assert round(row["r5_sd"], 2) == 2.83
    assert row["gains"][-1] == 2.0                    # 第 10 轮相对第 9 轮的平均增量
    assert abs(row["yuan_per_solve_with_r0"] - 0.2) < 1e-9   # 1M 输入 × 0.2 元 ÷ 平均 1 题
    assert "R10 均值 ± SD" in T.write_markdown([row], [])
