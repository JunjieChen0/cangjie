import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import reproduce_offline as R  # noqa: E402


def test_diff_classifies_files():
    before = {"a.md": "1", "b.json": "2", "c.png": "3"}
    after = {"a.md": "1", "b.json": "9", "d.md": "4"}
    assert R.diff(before, after) == {"same": ["a.md"], "changed": ["b.json"], "missing": ["c.png"], "new": ["d.md"]}


def test_offline_env_blanks_every_api_key():
    assert all(R.OFFLINE_ENV[k] == "" for k in ("LLM_API_KEY", "UNISOUND_API_KEY"))
    assert all("127.0.0.1:9" in R.OFFLINE_ENV[k] for k in ("LLM_BASE_URL", "UNISOUND_BASE_URL", "RAG2_URL"))
