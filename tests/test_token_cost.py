import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import token_cost as T  # noqa: E402

DB, DS, GLM = "doubao-seed-2-0-mini-260428", "deepseek-v4-1-flash-261017", "glm-5-3-flash-260828"


def test_category_by_directory():
    assert T.category("results/stage3/runs") == "stage3"
    assert T.category("results/stage3/pilot/r0") == "pilot"
    assert T.category("results/original30/r0") == "original30"
    assert T.category("results/original30/pilot/runs") == "pilot"
    assert T.category("results/rounds10/runs") == "rounds10"
    assert T.category("results/review/runs") == "review" and T.category("results/review/pilot/r0") == "pilot"
    assert T.category("results/ablation") == "early" and T.category("results/try") == "early"


def test_usd_is_domestic_list_price_converted_at_one_rate():
    assert T.cny_cost(DS, 1_000_000, 1_000_000) == 2.0 + 8.0             # DeepSeek 高峰价
    assert abs(T.usd_cost(DS, 1_000_000, 1_000_000) - 10.0 / 6.67) < 1e-12
    assert abs(T.cny_cost(GLM, 1_000_000, 1_000_000) - 3.6) < 1e-12
    assert T.cny_cost("u2-flash", 1_000_000, 0) == 1.0                   # 云知声原价


def _summary(path, model, pin, pout):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"model_resolved": model, "total_prompt_tokens": pin, "total_completion_tokens": pout}, f)


def test_load_and_aggregate_skip_empty_and_selftest(tmp_path):
    r = tmp_path / "results"
    _summary(str(r / "stage3/runs/a.summary.json"), DB, 1_000_000, 0)
    _summary(str(r / "stage3/pilot/runs/a.summary.json"), DS, 0, 1_000_000)
    _summary(str(r / "reeval/x.summary.json"), DB, 0, 0)                       # 只重新评测，无 token
    _summary(str(r / "try/stage3_selftest/runs/b.summary.json"), DB, 5, 5)     # 自测
    rows = T.load_usage(str(tmp_path))
    assert sorted((x["category"], x["model"]) for x in rows) == [("pilot", DS), ("stage3", DB)]
    lines = {(x["category"], x["model"]): x for x in T.aggregate(rows)}
    assert lines[("formal", "all")]["cny"] == 0.2 and lines[("formal", "all")]["runs"] == 1
    assert lines[("total", "all")]["cny"] == 8.2 and lines[("total", "all")]["usd"] == round(8.2 / 6.67, 2)
    assert lines[("pilot", DS)]["completion_tokens"] == 1_000_000


def test_rag2_rewrite_tokens_are_costed_at_rewriter_price(tmp_path):
    p = tmp_path / "results/review/runs/x.summary.json"
    os.makedirs(p.parent)
    p.write_text(json.dumps({"model_resolved": DS, "total_prompt_tokens": 1_000_000, "total_completion_tokens": 0,
                             "rewrite_model": DB, "total_rewrite_prompt_tokens": 0,
                             "total_rewrite_completion_tokens": 1_000_000}), encoding="utf-8")
    rows = T.load_usage(str(tmp_path))
    assert [(r["model"], r["category"]) for r in rows] == [(DS, "review"), (DB, "review")]
    lines = {(x["category"], x["model"]): x for x in T.aggregate(rows)}
    assert lines[("review", "all")]["cny"] == 2.0 + 2.0          # DeepSeek 输入 1M×2 元 + 改写输出 1M×2 元
