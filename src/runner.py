"""在本机（Windows/Linux）用 cjc 编译并运行仓颉代码，判定结果。

判定逻辑与 CangjieBench 官方 sandbox (app.py) 保持一致，保证结果可比。
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, asdict

ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
IS_WIN = sys.platform.startswith("win")
EXE_NAME = "main.exe" if IS_WIN else "main"


def clean(text: str | None) -> str:
    return ANSI_ESCAPE_RE.sub("", text or "")


@dataclass
class RunResult:
    passed: bool
    failure_kind: str          # passed / compile_error / test_failure / runtime_exception / nonzero_exit / timeout
    compile_stderr: str = ""
    run_stdout: str = ""
    run_stderr: str = ""
    return_code: int | None = None

    def to_dict(self):
        return asdict(self)

    @property
    def feedback(self) -> str:
        """给大模型看的错误信息（截断，避免 token 爆炸）。"""
        if self.failure_kind == "compile_error":
            msg = self.compile_stderr
        elif self.failure_kind == "timeout":
            msg = "Execution timed out (possible infinite loop)."
        else:
            msg = (self.run_stderr + "\n" + self.run_stdout).strip()
        return msg[:3000]


def compile_and_run(code: str, compile_timeout: int = 60, run_timeout: int = 10) -> RunResult:
    tmpdir = tempfile.mkdtemp(prefix="cj_")
    try:
        src = os.path.join(tmpdir, "main.cj")
        with open(src, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            c = subprocess.run(
                ["cjc", "main.cj", "-o", EXE_NAME],
                cwd=tmpdir, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=compile_timeout,
            )
        except subprocess.TimeoutExpired:
            return RunResult(False, "timeout", compile_stderr="compile timeout")
        cerr = clean(c.stderr) + clean(c.stdout)
        exe = os.path.join(tmpdir, EXE_NAME)
        if c.returncode != 0 or not os.path.exists(exe):
            return RunResult(False, "compile_error", compile_stderr=cerr, return_code=c.returncode)
        try:
            r = subprocess.run(
                [exe], cwd=tmpdir, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=run_timeout,
            )
        except subprocess.TimeoutExpired:
            return RunResult(False, "timeout", compile_stderr=cerr)
        out, err = clean(r.stdout), clean(r.stderr)
        low_out, low_err = out.lower(), err.lower()
        if "test failed" in low_err or "test failed" in low_out or "fail" in low_out:
            kind = "test_failure"
        elif r.returncode != 0:
            kind = "runtime_exception" if ("exception" in low_err) else "nonzero_exit"
        else:
            kind = "passed"
        return RunResult(kind == "passed", kind, cerr, out, err, r.returncode)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
