"""第 2 阶段改动的单元测试：全部测试驱动的反馈合并、文档检索、温度记录、提示模板。不调用 API、不编译。"""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import doc_retrieval as D  # noqa: E402
import llm  # noqa: E402
import prompts as P  # noqa: E402
import repair  # noqa: E402
from runner import RunResult  # noqa: E402


def compile_err(msg):
    return RunResult(False, "compile_error", compile_stderr=msg)


def failed_run(out):
    return RunResult(False, "test_failure", run_stdout=out)


OK = RunResult(True, "passed")


# ---------- aggregate_feedback ----------
def test_all_passed():
    r = repair.aggregate_feedback([OK, OK])
    assert r.passed and r.failure_kind == "passed" and r.status == [True, True]


def test_identical_compile_errors_reported_once():
    r = repair.aggregate_feedback([compile_err("E1"), compile_err("E1"), compile_err("E1")])
    assert r.failure_kind == "compile_error"
    assert r.feedback == "E1"
    assert r.status == [False, False, False]


def test_different_compile_errors_are_labelled_by_test():
    r = repair.aggregate_feedback([compile_err("E1"), OK, compile_err("E2")])
    assert "[with test #0]\nE1" in r.feedback and "[with test #2]\nE2" in r.feedback


def test_compile_error_takes_priority_over_test_failure():
    r = repair.aggregate_feedback([failed_run("fail"), compile_err("E1")])
    assert r.failure_kind == "compile_error" and r.feedback == "E1"


def test_failed_tests_listed_in_order_with_count():
    r = repair.aggregate_feedback([OK, failed_run("a fail"), failed_run("b fail")])
    assert r.feedback.startswith("2 of 3 tests failed.")
    assert r.feedback.index("[test #1") < r.feedback.index("[test #2")
    assert r.status == [True, False, False]


def test_feedback_truncated_to_cap():
    r = repair.aggregate_feedback([failed_run("fail " + "x" * 2900) for _ in range(3)])
    assert len(r.feedback) == repair.FEEDBACK_CAP


# ---------- repair_prompt ----------
def test_rag_prompt_includes_docs_and_records_titles(monkeypatch):
    monkeypatch.setattr(repair, "retrieve_for_feedback",
                        lambda fb: [{"title": "doc > ArrayList", "text": "use size", "score": 1.0}])
    text, meta = repair.repair_prompt(compile_err("error: x"), "rag")
    assert "[doc > ArrayList]" in text and "error: x" in text
    assert meta == {"retrieved": ["doc > ArrayList"]}


def test_existing_modes_return_empty_meta():
    for mode in ("blind", "raw", "hint"):
        text, meta = repair.repair_prompt(compile_err("error: x"), mode)
        assert text and meta == {}


def test_blind_prompt_v2_mentions_compilation():
    assert P.PROMPT_VERSION == 2
    assert "did not compile" in P.REPAIR_BLIND


# ---------- doc_retrieval ----------
def test_split_sections_tracks_heading_path():
    text = "# A\nintro\n## B\nbody b\n### C\nbody c\n## D\nbody d"
    chunks = D.split_sections(text, "f.md")
    assert [c["title"] for c in chunks] == ["f.md > A", "f.md > A > B", "f.md > A > B > C", "f.md > A > D"]


def test_tokenize_splits_camel_case_and_cjk():
    toks = D.tokenize("ArrayList 数组")
    assert "arraylist" in toks and "array" in toks and "list" in toks and "数" in toks


def test_bm25_ranks_matching_doc_first():
    bm = D.BM25([["foo", "bar"], ["arraylist", "size"], ["baz"]])
    s = bm.scores(["size"])
    assert s.index(max(s)) == 1 and s[0] == 0.0


def test_build_query_skips_warnings_and_keeps_source_lines():
    fb = ("error: expected '(' after 'if'\n ==> main.cj:3:5:\n  | \n3 |     if n == 0 {\n  |     ^\n\n"
          "warning: function 'sort' is deprecated\n ==> main.cj:5:12:\n5 |     xs.sort()\n")
    q = D.build_query(fb)
    assert "if n == 0" in q and "deprecated" not in q and "xs.sort" not in q


def test_build_query_falls_back_to_raw_text_for_runtime_errors():
    assert D.build_query("Exception: index out of range") == "Exception: index out of range"


def test_format_docs_respects_budget():
    chunks = [{"title": "t", "text": "x" * 5000}] * 3
    assert len(D.format_docs(chunks, max_chars=900)) <= 900 + 4  # 块间分隔符


# ---------- llm.chat 温度记录 ----------
def test_chat_records_fallback_temperature(monkeypatch):
    calls = []

    def create(model, messages, temperature):
        calls.append(temperature)
        if temperature != 1.0:
            raise ValueError("`temperature` only 1 is allowed for this model")
        return SimpleNamespace(usage=SimpleNamespace(prompt_tokens=3, completion_tokens=4),
                               choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))])

    fake = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(llm, "_client", fake)
    text, usage = llm.chat([{"role": "user", "content": "hi"}], model="m", temperature=0.0)
    assert text == "ok" and calls == [0.0, 1.0]
    assert usage == {"prompt_tokens": 3, "completion_tokens": 4, "temperature": 1.0}
