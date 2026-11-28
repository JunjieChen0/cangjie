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


def test_review_matrix_covers_new_models_kimi_and_deepseek_ce_syntax():
    r0, rep = M.expand_matrix("review")
    names = {j.name for j in rep}
    assert len(names) == len(rep) == len(M.NEW_MODELS) * 81 + 81 + 12 + len([j for j in rep if j.feedback in M.AGENT_ARMS or j.feedback == "rag2"])
    assert all(j.r0_name in {x.name for x in r0} for j in rep if j.init_matrix is None)
    for m in M.NEW_MODELS + ("kimik31p",):
        assert {f"{m}_{ds}_{p}_rag_rep3" for ds in ("he", "ce", "or") for p in ("direct", "syntax")} <= names
    kimi = [j for j in rep if j.model == "kimik31p"]
    assert all(j.temp == M.KIMI_TEMP and j.env["LLM_TIMEOUT"] == M.KIMI_REVIEW_TIMEOUT for j in kimi)
    assert {f"ds_v41f_ce_syntax_{fb}_rep1" for fb in M.FOUR} <= names
    assert M.out_dir(False, "review").replace("\\", "/").endswith("results/review/")


def test_agent_jobs_reuse_existing_r0_and_set_step_budget():
    r0, rep = M.expand_matrix("review")
    agents = [j for j in rep if j.feedback in M.AGENT_ARMS]
    assert len(agents) == (len(M.NEW_MODELS) + 1) * 3 * 2 * 2 * 3 + 2 * (2 * 2 + 1) * 2 * 3 + 2 * 3 + 2 * 3
    j = next(x for x in agents if x.name == "doubao_mini_he_direct_agent15_rep2")
    assert j.init_matrix == "stage3" and j.rounds == 15
    cmd = M.build_cmd(j, M.out_dir(False, "review"), False, 4)
    assert cmd[cmd.index("--feedback") + 1] == "agent" and cmd[cmd.index("--rounds") + 1] == "15"
    assert cmd[cmd.index("--init") + 1].replace("\\", "/").endswith("results/stage3/r0/doubao_mini_he_direct_r0.jsonl")
    assert "doubao_mini_he_direct_r0" not in {x.name for x in r0}     # 不在 review 中重复生成第 0 轮
    k = next(x for x in agents if x.name == "ds_v41f_or_syntax_agent_rep1")
    assert M.r0_path(k, "unused", False).replace("\\", "/").endswith("results/original30/r0/ds_v41f_or_syntax_r0.jsonl")


def test_rag2_jobs_cover_all_models_and_reuse_r0():
    r0, rep = M.expand_matrix("review")
    rag2 = [j for j in rep if j.feedback == "rag2"]
    assert len(rag2) == (len(M.NEW_MODELS) + 1) * 3 * 2 * 3 + 2 * (2 * 2 + 1) * 3 + 3 + 3
    j = next(x for x in rag2 if x.name == "ds_v41f_he_direct_rag2_rep1")
    cmd = M.build_cmd(j, M.out_dir(False, "review"), False, 4)
    assert cmd[cmd.index("--feedback") + 1] == "rag2" and cmd[cmd.index("--rounds") + 1] == "5"
    assert j.init_matrix == "stage3"


# ---------- 修订实验（docs/修订实验方案.md）----------
def test_revision_matrix_has_fixed15_and_kimi_linux_reruns_only():
    r0, rep = M.expand_matrix("revision")
    assert r0 == []                                   # 第 0 轮全部复用已有矩阵
    names = {j.name for j in rep}
    assert len(names) == len(rep) == 3 * 2 * 3 + 2 * 3 + 3 * 3
    assert {f"{m}_ce_direct_{fb}_rep{r}" for m in ("doubao21l", "gpt6l", "ds_v41f")
            for fb in ("raw15", "rag15") for r in M.REPS} <= names
    assert {f"kimik31p_ce_direct_{fb}_rep{r}" for fb in ("blind", "agent") for r in M.REPS} <= names
    assert M.out_dir(False, "revision").replace("\\", "/").endswith("results/revision/")


def test_fixed15_jobs_use_15_rounds_base_feedback_and_shared_r0():
    _, rep = M.expand_matrix("revision")
    base = M.out_dir(False, "revision")
    for name, fb, r0_dir in (("doubao21l_ce_direct_raw15_rep1", "raw", "review"),
                             ("gpt6l_ce_direct_rag15_rep3", "rag", "review"),
                             ("ds_v41f_ce_direct_raw15_rep2", "raw", "stage3")):
        j = next(x for x in rep if x.name == name)
        assert j.rounds == 15 and j.temp == M.TEMP and j.env == {"LLM_TIMEOUT": "1800"}
        cmd = M.build_cmd(j, base, False, 4)
        assert cmd[cmd.index("--feedback") + 1] == fb and cmd[cmd.index("--rounds") + 1] == "15"
        assert "--all-tests" in cmd
        model = name.split("_ce_")[0]
        assert cmd[cmd.index("--init") + 1].replace("\\", "/").endswith(
            f"results/{r0_dir}/r0/{model}_ce_direct_r0.jsonl")
        assert cmd[cmd.index("-o") + 1].replace("\\", "/").endswith(f"results/revision/runs/{name}.jsonl")


def test_kimi_reruns_match_review_protocol():
    _, rep = M.expand_matrix("revision")
    kimi = [j for j in rep if j.model == "kimik31p"]
    assert len(kimi) == 6
    assert all(j.temp == M.KIMI_TEMP and j.env == {"LLM_TIMEOUT": M.KIMI_REVIEW_TIMEOUT} for j in kimi)
    assert all(j.rounds == M.ROUNDS and j.init_matrix == "review" for j in kimi)
    cmd = M.build_cmd(next(j for j in kimi if j.feedback == "agent"), M.out_dir(False, "revision"), False, 4)
    assert cmd[cmd.index("--feedback") + 1] == "agent" and cmd[cmd.index("--rounds") + 1] == "5"


def test_gpt_redo_matches_review_jobs_except_r0_and_output():
    """方案第十二节：MyUSAPI 补跑的 raw / rag / agent15 与 review 同名组参数相同，第 0 轮取 review，输出到 revision。"""
    _, rev = M.expand_matrix("revision")
    _, old = M.expand_matrix("review")
    redo = [j for j in rev if j.model == "gpt6l" and j.feedback in M.REVISION_GPT_REDO]
    assert len(redo) == 9
    rb, ob = M.out_dir(False, "revision"), M.out_dir(False, "review")
    for j in redo:
        o = next(x for x in old if x.name == j.name)
        assert (j.temp, j.rounds, j.env, j.feedback) == (o.temp, o.rounds, o.env, o.feedback)
        assert j.init_matrix == "review" and o.init_matrix is None
        a, b = M.build_cmd(j, rb, False, 4), M.build_cmd(o, ob, False, 4)
        assert a[a.index("--init") + 1] == b[b.index("--init") + 1]          # 同一份共享第 0 轮
        assert a[a.index("-o") + 1].replace("\\", "/").endswith(f"results/revision/runs/{j.name}.jsonl")
        strip = lambda c: [x for i, x in enumerate(c) if i not in (c.index("-o") + 1,)]   # noqa: E731
        assert strip(a) == strip(b)


def test_revision_does_not_change_review_matrix():
    _, rep = M.expand_matrix("review")
    assert not [j for j in rep if j.feedback in ("raw15", "rag15")]
