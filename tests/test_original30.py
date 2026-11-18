import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import data  # noqa: E402
import run_matrix as M  # noqa: E402


def test_load_original30_has_30_problems_with_expected_fields():
    ds = data.load_original30()
    assert sorted(ds) == list(range(1000, 1030))
    assert all(set(v) == {"id", "prompt", "solution", "test"} for v in ds.values())


def test_original_matrix_size_and_names():
    r0, rep = M.expand_matrix("original")
    assert len(r0) == 5 and len(rep) == 54
    assert len({j.name for j in rep}) == 54
    assert all(j.ds == "or" for j in r0 + rep)
    s_r0, s_rep = M.expand_matrix()
    assert not {j.name for j in r0 + rep} & {j.name for j in s_r0 + s_rep}


def test_default_matrix_unchanged():
    r0, rep = M.expand_matrix()
    assert len(r0) == 9 and len(rep) == 107


def test_original_cmd_uses_original_dataset_and_own_dir():
    _, rep = M.expand_matrix("original")
    job = next(j for j in rep if j.name == "doubao_mini_or_syntax_rag_rep3")
    base = M.out_dir(pilot=False, matrix="original")
    assert base.rstrip(os.sep).endswith(os.path.join("results", "original30"))
    cmd = M.build_cmd(job, base, pilot=False, workers=4)
    assert cmd[cmd.index("--dataset") + 1] == "original"
    assert "--all-tests" not in cmd
    assert cmd[cmd.index("--init") + 1] == os.path.join(base, "r0", "doubao_mini_or_syntax_r0.jsonl")


def test_kimi_original_jobs_use_temperature_one():
    _, rep = M.expand_matrix("original")
    kimi = [j for j in rep if j.model == "kimik31p"]
    assert len(kimi) == 6 and all(j.temp == 1.0 and j.prompt == "direct" for j in kimi)


def test_is_done_expects_30_for_original(tmp_path):
    r0, _ = M.expand_matrix("original")
    p = M.output_path(r0[0], str(tmp_path)).replace(".jsonl", "") + ".summary.json"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write('{"n": 30, "errors": 0}')
    assert M.is_done(r0[0], str(tmp_path), pilot=False)
