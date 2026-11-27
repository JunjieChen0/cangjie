import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import repair  # noqa: E402
from runner import RunResult  # noqa: E402


def test_parse_action_prefers_code_then_search():
    assert repair.parse_action("Let me fix.\n```cangjie\nfunc f() {}\n```") == ("test", "func f() {}\n")
    assert repair.parse_action("SEARCH: ArrayList add method") == ("search", "ArrayList add method")
    assert repair.parse_action("`SEARCH: range syntax`") == ("search", "range syntax")
    assert repair.parse_action("I think the bug is ...") == ("invalid", "")
    assert repair.parse_action("SEARCH: x\n```cangjie\ncode\n```")[0] == "test"


def _run(replies, results, rounds=5):
    """用固定回复和固定评测结果驱动 agent_steps，返回 (最终结果, 代码, 记录, 发给模型的观察)。"""
    replies, results, history, observations = list(replies), list(results), [], []

    def ask_raw(obs):
        observations.append(obs)
        return replies.pop(0)

    def record(rnd, res, code, **extra):
        history.append({"round": rnd, "failure_kind": res.failure_kind, "code": code, **extra})

    orig_eval, orig_search = repair.evaluate, repair.search_docs
    repair.evaluate = lambda code, item, all_tests: results.pop(0)
    repair.search_docs = lambda q: [{"title": f"doc for {q}", "text": "..."}]
    try:
        args = SimpleNamespace(rounds=rounds, all_tests=False)
        r0 = RunResult(False, "compile_error", compile_stderr="error: undeclared identifier 'abs'")
        res, code = repair.agent_steps({}, args, r0, "c0", ask_raw, lambda c: c.strip(), record)
    finally:
        repair.evaluate, repair.search_docs = orig_eval, orig_search
    return res, code, history, observations


def test_agent_searches_then_tests_and_stops_on_pass():
    res, code, hist, obs = _run(["SEARCH: abs function", "```cangjie\nfixed\n```"], [RunResult(True, "passed")])
    assert res.passed and code == "fixed"
    assert [h["action"] for h in hist] == ["search", "test"]
    assert hist[0]["retrieved"] == ["doc for abs function"]
    assert "undeclared identifier" in obs[0] and "5 action(s) left" in obs[0]
    assert 'Search results for "abs function"' in obs[1] and "4 action(s) left" in obs[1]


def test_agent_budget_counts_every_model_call():
    res, code, hist, obs = _run(["hmm", "SEARCH: q", "```cangjie\nv1\n```"],
                                [RunResult(False, "compile_error", compile_stderr="error: x")], rounds=3)
    assert not res.passed and code == "v1" and len(obs) == 3
    assert [h["action"] for h in hist] == ["invalid", "search", "test"]
    assert "neither" in obs[1]


def test_solve_records_served_models_per_problem(monkeypatch):
    served = iter(["m-a", "m-b", "m-a"])
    monkeypatch.setattr(repair, "chat", lambda messages, model, temperature: (
        "```cangjie\nfunc f() {}\n```",
        {"prompt_tokens": 1, "completion_tokens": 1, "temperature": temperature, "served_model": next(served)}))
    results = iter([RunResult(False, "compile_error", compile_stderr="e"), RunResult(False, "compile_error", compile_stderr="e"),
                    RunResult(True, "passed")])
    monkeypatch.setattr(repair, "evaluate", lambda code, item, all_tests: next(results))
    args = SimpleNamespace(strip_main=False, model="m", temperature=0.3, feedback="raw", rounds=5,
                           compile_only_feedback=False, all_tests=False, prompt="direct")
    row = repair.solve({"id": 1, "prompt": "q"}, args, "", None)
    assert row["passed"] and row["served_models"] == ["m-a", "m-b"]
