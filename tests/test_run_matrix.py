import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import run_matrix as M  # noqa: E402


def test_matrix_size_matches_plan():
    r0, rep = M.expand_matrix()
    assert len(r0) == 9
    assert len(rep) == 107
    assert len({j.name for j in rep}) == 107   # 名称唯一


def test_every_repair_has_its_r0():
    r0, rep = M.expand_matrix()
    names = {j.name for j in r0}
    assert all(j.r0_name in names for j in rep)


def test_classeval_jobs_use_all_tests_and_init():
    _, rep = M.expand_matrix()
    job = next(j for j in rep if j.name == "ds_v41f_ce_direct_rag_rep2")
    cmd = M.build_cmd(job, "B", pilot=False, workers=4)
    assert "--all-tests" in cmd and "--init" in cmd
    assert cmd[cmd.index("--init") + 1].endswith(os.path.join("r0", "ds_v41f_ce_direct_r0.jsonl"))
    assert cmd[cmd.index("--feedback") + 1] == "rag"
    assert cmd[cmd.index("--temperature") + 1] == "0.3"


def test_r0_job_has_zero_rounds_and_no_init():
    r0, _ = M.expand_matrix()
    cmd = M.build_cmd(r0[0], "B", pilot=False, workers=4)
    assert cmd[cmd.index("--rounds") + 1] == "0" and "--init" not in cmd


def test_kimi_uses_temperature_one_and_long_timeout_for_classeval():
    r0, rep = M.expand_matrix()
    kimi = [j for j in rep if j.model == "kimik31p"]
    assert len(kimi) == 8 and all(j.temp == 1.0 for j in kimi)
    ce = [j for j in kimi + r0 if j.model == "kimik31p" and j.ds == "ce"]
    assert ce and all(j.env == {"LLM_TIMEOUT": "600"} for j in ce)


def test_deepseek_classeval_uses_long_timeout():
    r0, rep = M.expand_matrix()
    ds_ce = [j for j in r0 + rep if j.model == "ds_v41f" and j.ds == "ce"]
    assert len(ds_ce) == 13 and all(j.env == {"LLM_TIMEOUT": "600"} for j in ds_ce)
    assert all(j.env == {} for j in r0 + rep if j.model == "doubao_mini")


def test_compile_only_flag_and_pilot_limit():
    _, rep = M.expand_matrix()
    job = next(j for j in rep if j.compile_only)
    cmd = M.build_cmd(job, "B", pilot=True, workers=2)
    assert "--compile-only-feedback" in cmd
    assert cmd[cmd.index("--limit") + 1] == str(M.PILOT_LIMIT)


def test_select_keeps_needed_r0():
    r0, rep = M.select(*M.expand_matrix(), "doubao_mini_he_syntax")
    assert {j.name for j in r0} == {"doubao_mini_he_syntax_r0"}
    assert len(rep) == 12


def _write_summary(base, job, **s):
    p = M.output_path(job, str(base)).replace(".jsonl", "") + ".summary.json"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(s, f)


def test_is_done_requires_full_n_and_zero_errors(tmp_path):
    r0, _ = M.expand_matrix()
    job = r0[0]
    assert not M.is_done(job, str(tmp_path), pilot=False)
    _write_summary(tmp_path, job, n=164, errors=1)
    assert not M.is_done(job, str(tmp_path), pilot=False)
    _write_summary(tmp_path, job, n=164, errors=0)
    assert M.is_done(job, str(tmp_path), pilot=False)
    assert not M.is_done(job, str(tmp_path), pilot=True)   # 试跑要求 n = 10
