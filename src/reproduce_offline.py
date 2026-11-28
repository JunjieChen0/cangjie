"""离线复现验收（投稿闸门 4）：不调用任何模型 API，只用归档的原始结果重新生成全部统计输出，并与现有文件逐一比对。

用法（在仓库根目录或解压后的复现包根目录）：
  python src/reproduce_offline.py
结果：每个输出文件「一致 / 不一致 / 新生成」；文本输出（md / json）有任何不一致即返回非零退出码。
图片（png）只报告是否逐字节相同，不作为判定依据（不同 matplotlib 版本的元数据可能不同）。
注意：脚本会就地重新生成输出；有不一致时可用 git diff 查看差异。

为确保不调用 API：子进程中清空各 API key（.env 中的值不会覆盖已设置的空值），并把服务地址指向本机不可用端口。
"""
from __future__ import annotations

import glob
import hashlib
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEPS = (["stage3_stats.py"], ["stage3_stats.py", "--matrix", "original"], ["rounds10_stats.py"],
         ["residual_failures.py"], ["extra_stats.py"], ["token_cost.py"], ["manual_check_agreement.py"],
         ["review_stats.py"], ["sensitivity_report.py"], ["robustness_checks.py"], ["posthoc_checks.py"],
         ["case_examples.py"], ["heldout_eval.py", "stats"],
         ["plot_figures.py"])
OUTPUT_GLOBS = ("results/stats/*.md", "results/stats/*.json", "results/case_examples.md",
                "results/retrieval_eval/manual_check_agreement.*", "results/figures/*.png")
OFFLINE_ENV = {"LLM_API_KEY": "", "UNISOUND_API_KEY": "", "LLM_BASE_URL": "http://127.0.0.1:9/v1",
               "UNISOUND_BASE_URL": "http://127.0.0.1:9/v1", "RAG2_URL": "http://127.0.0.1:9/search",
               "HF_HUB_OFFLINE": "1", "PYTHONIOENCODING": "utf-8"}


def snapshot(root: str = ROOT) -> dict[str, str]:
    out = {}
    for pat in OUTPUT_GLOBS:
        for p in glob.glob(os.path.join(root, pat)):
            with open(p, "rb") as f:
                out[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(f.read()).hexdigest()
    return out


def diff(before: dict[str, str], after: dict[str, str]) -> dict[str, list[str]]:
    return {"same": sorted(k for k in before if after.get(k) == before[k]),
            "changed": sorted(k for k in before if k in after and after[k] != before[k]),
            "missing": sorted(k for k in before if k not in after),
            "new": sorted(k for k in after if k not in before)}


def main():
    before = snapshot()
    env = dict(os.environ, **OFFLINE_ENV)
    for step in STEPS:
        r = subprocess.run([sys.executable, "-X", "utf8", os.path.join(ROOT, "src", step[0]), *step[1:]],
                           cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8")
        print(f"{'✓' if r.returncode == 0 else '✗'} {' '.join(step)}")
        if r.returncode != 0:
            print(r.stderr[-2000:])
            sys.exit(1)
    d = diff(before, snapshot())
    text_bad = [k for k in d["changed"] + d["missing"] if not k.endswith(".png")]
    print(f"\n一致 {len(d['same'])} 个；不一致 {len(d['changed'])} 个；缺失 {len(d['missing'])} 个；新生成 {len(d['new'])} 个")
    for kind in ("changed", "missing", "new"):
        for k in d[kind]:
            print(f"  {kind}: {k}")
    if text_bad:
        print("\n✗ 文本输出与归档不一致：离线复现未通过")
        sys.exit(1)
    print("\n✓ 全部文本输出逐字节复现" + ("（部分图片元数据不同，不影响判定）" if d["changed"] else ""))


if __name__ == "__main__":
    main()
