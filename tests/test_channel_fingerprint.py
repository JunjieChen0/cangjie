import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import channel_fingerprint as F  # noqa: E402


def call(i, rep, toks, pt=100, lp=-0.1):
    return {"id": i, "rep": rep, "served_model": "m", "prompt_tokens": pt, "content": "".join(toks),
            "tokens": [{"t": t, "lp": lp, "top": []} for t in toks]}


def run(name, toks_fn, pt_fn=lambda i: 100, lp=-0.1, temp=0.0):
    return {"name": name, "temperature": temp,
            "calls": [call(i, r, toks_fn(i, r), pt_fn(i), lp) for i in range(F.N_PROMPTS) for r in range(F.REPS)]}


def test_identical_channels_pass():
    a = run("a", lambda i, r: ["x", str(i)])
    b = run("b", lambda i, r: ["x", str(i)], lp=-0.12)
    res = F.compare(a, b)
    assert res["checks"] == {"C1_prompt_tokens_equal": True, "C2_logprob_close": True, "C3_cross_agreement": True}
    assert res["verdict"] == "一致"


def test_prompt_token_mismatch_fails():
    res = F.compare(run("a", lambda i, r: ["x"]), run("b", lambda i, r: ["x"], pt_fn=lambda i: 100 + (i == 3)))
    assert res["checks"]["C1_prompt_tokens_equal"] is False and res["verdict"] == "不一致"


def test_logprob_shift_fails():
    res = F.compare(run("a", lambda i, r: ["x", "y"]), run("b", lambda i, r: ["x", "y"], lp=-0.5))
    assert res["checks"]["C2_logprob_close"] is False and res["verdict"] == "不一致"


def test_cross_text_divergence_fails():
    res = F.compare(run("a", lambda i, r: ["x", "y"]), run("b", lambda i, r: ["x", "z"]))
    assert res["checks"]["C3_cross_agreement"] is False
    assert res["cross"]["identical_rate"] == 0.0


def test_no_logprobs_and_sampling_skip_c2_c3():
    a, b = run("a", lambda i, r: ["x"], temp=1.0), run("b", lambda i, r: ["x"], temp=1.0)
    for c in a["calls"] + b["calls"]:
        c["tokens"] = None
    res = F.compare(a, b)
    assert res["checks"]["C2_logprob_close"] is None and res["checks"]["C3_cross_agreement"] is None
    assert res["verdict"] == "一致"


def test_pair_stats_prefix():
    s = F.pair_stats(call(0, 0, ["a", "b", "c"]), call(0, 1, ["a", "b", "d"]))
    assert s["prefix"] == 2 and not s["identical"] and len(s["lp_diffs"]) == 2


def test_requests_match_round0():
    m = F.messages_for({"prompt": "class X {}"})
    assert m[0]["content"] == F.P.SYSTEM and m[1]["content"] == F.P.DIRECT.format(question="class X {}")
    assert len(F.task_ids()) == F.N_PROMPTS
