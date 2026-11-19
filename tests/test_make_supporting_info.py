import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import check_numbers as C  # noqa: E402
import make_supporting_info as S  # noqa: E402

CMP = {"model": "doubao_mini", "ds": "or", "prompt": "direct", "a": "hint", "b": "raw", "n": 30, "n_discordant": 10,
       "diff": 16.67, "ci_lo": 7.78, "ci_hi": 26.67, "p": 0.0012, "p_holm": 0.0192, "mcnemar_per_rep": [0.7266, 0.00001]}


def test_coding_en_maps_categories_and_marks_pure_timeouts():
    c = {"category": "题意理解", "subtype": "跨方法状态依赖"}
    assert S.coding_en(["test_failure"], c) == ("misread explicit specification", "cross-method state dependency")
    assert S.coding_en(["api_timeout"], c)[0] == "timeout"
    assert S.coding_en(["test_failure"], None) == ("", "")


def test_every_chinese_label_has_an_english_name():
    for row in S.load_coding().values():
        assert row["category"] in S.CATEGORY and row["subtype"] in S.SUBTYPE and row["evidence_en"]


def test_comparison_rows_are_english_and_pass_check_numbers():
    lines = S.comparison_table([CMP])
    assert lines[2].startswith("| Doubao-Seed-2.0-mini | Original-30 | direct | hint vs raw | 30 | 10 |")
    assert "<0.0001" in lines[2]
    known = C.known_values([{"comparisons": [CMP]}])
    assert C.check_text("\n".join(lines), known) == []


def test_hint_rules_table_lists_every_rule_and_escapes_pipes():
    lines = S.hint_rules_section([("a", r"x|y", "use `if (x) {}`"), ("b", "z", "h|i")])
    rows = [line for line in lines if line.startswith(("| 1 ", "| 2 "))]
    assert len(rows) == 2 and r"x\|y" in rows[0] and r"h\|i" in rows[1]
    assert "The 2 hand-curated rules" in lines[2]
