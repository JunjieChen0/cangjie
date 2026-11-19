# 仓颉代码生成：低成本编译反馈修复研究

> 工作题目：**《面向低资源语言仓颉的轻量级编译反馈修复：用几轮对话逼近 Agent 的效果？》**
> 目标期刊：*Software: Practice and Experience*（SPE）

## 一句话
CangjieBench（ESEM 2026）发现：语法约束提示一次生成能做到 40–64% 的通过率，GPT-5 + Codex Agent 能做到 85%，但 token 消耗极高；用便宜模型的 Agent 只有 25–39%。
**本项目研究中间地带**：不使用 Agent 框架，只做"生成 → cjc 编译 → 把报错喂回去"的几轮循环，
在 HumanEval-Cangjie（164 题，函数级）和 ClassEval-Cangjie（84 题，类级）上回答**哪种反馈最有用、几轮够用、花多少钱**。

## 主要结论
完整数字、显著性检验与有效性威胁见 [docs/实验汇总报告.md](docs/实验汇总报告.md)。

- **多轮修复收益大、收敛快**：强模型（DeepSeek-V4.1-Flash、Kimi-K3.1-Pro）在 HumanEval 上 1–3 轮即接近 100%。
- **知识提示（hint）的优势有边界**：只在"轻量模型（Doubao-Seed-2.0-Mini）+ 函数级任务 + `direct` 起点"下显著优于原始报错（raw）。在共享第 0 轮的 3 次重复中，hint 为 55.69±1.41%，raw 为 41.05±1.76%，差值 +14.63 个百分点，95% CI [9.96, 19.72]。ClassEval 与强模型上两者无显著差异。
- **不依赖测试信息**：只给编译错误、不给测试结果时，hint 仍为 50.00%，raw 为 32.93%。
- **优于独立重采样**：同模型独立生成 6 次（pass@6）只有 17.07%。
- **ClassEval 采用官方全部测试口径**：只看集成测试会高估，268 份通过集成测试的代码中有 107 份（39.9%）未通过方法级测试。

## 目录
```
src/
  runner.py            本地 cjc 编译运行 + 判定（与 CangjieBench 官方判定一致，已验证）
  data.py              加载 CangjieBench HumanEval / ClassEval，以及新题集 Original-30
  evaluate.py          评测 solutions jsonl
  llm.py               OpenAI 兼容 API 调用（模型拒收 temperature=0 时自动回退到 1）
  prompts.py           提示词：初始提示（direct / syntax）+ 四种修复反馈（blind / raw / hint / rag）
  repair_hints.py      "报错 → 仓颉知识"规则库
  doc_retrieval.py     rag 反馈：用报错从官方文档（CangjieDocCorpus）BM25 检索片段
  repair.py            核心实验：生成 + 多轮修复（含只给编译错误、共享第 0 轮、ClassEval 全部测试驱动等选项）
  sample_passk.py      独立重采样基线（pass@k）
  run_matrix.py        实验矩阵批量运行器：第 3 阶段与新题集（共享第 0 轮、3 次重复、断点续跑、自动检查）
  reeval_classeval.py  ClassEval 全部测试复评（官方 pass_rate 口径）
  analyze.py           统计汇总、McNemar 检验、错误类别修复率
  split_eval.py        5:5 题目划分一致性检查
  extra_stats.py       零成本补充统计：Test 半区、Holm 校正、成本、截断率
  stage3_stats.py      第 3 阶段 / 新题集统计：3 次重复均值±sd、按题置换检验与 bootstrap CI、Holm 校正、成本、去掉判定不稳定题的敏感性分析；Kimi 的 API 超时按未通过计
  plot_figures.py      生成论文插图
  mine_errors.py       从公开失败样本中统计高频 cjc 报错（零成本）
  postprocess.py       零成本后处理实验
tests/                 单元测试（pytest）
data/original30/       新写的 30 道题（控制数据污染），含登记表与检查记录，见其中 README.md
external/CangjieBench/ 数据集与公开结果（MIT 许可，git clone 而来，不进 git）
results/
  exp/                 18 组主实验（*.summary.json 进 git，原始 *.jsonl 不进 git）
  ablation/            9 组补强实验
  reeval/              ClassEval 全部测试复评结果
  stats/               零成本补充统计（extra_stats.md）
  stage3/              第 3 阶段实验（summary.json 进 git）
  original30/          新题集实验（summary.json 进 git）
  figures/             论文插图 fig1–fig4
  repro/               官方结果复现
  try/                 试跑与中止的实验（不进 git）
docs/
  实验汇总报告.md       全部实验结果与结论（写论文主要参考）
  RAG检索人工检查.md     rag 检索质量的人工抽查（实验前）
  第3阶段实验清单.md     第 3 阶段实验的运行步骤（给运行实验的作者）
  研究计划.md           研究问题、实验设计
  项目计划书.md
```

## 快速开始
```powershell
pip install -r requirements.txt

# 1. 环境自检：官方参考答案应 164/164 通过
python src/evaluate.py --reference

# 2. 复现论文数字：DeepSeek-V3 语法约束（论文 40.9%，本地 40.85%）
python src/evaluate.py -i external/CangjieBench/Results/Text_to_Code/Syntax_Constrained/DeepSeek-V3_HumanEval.jsonl -o results/repro/ds_v3_syntax.records.jsonl

# 3. 高频报错统计（零成本）
python src/mine_errors.py
```

在项目根目录新建 `.env` 配置大模型 API（已在 `.gitignore` 中，**不要提交**），`llm.py` 会自动读取：
```
LLM_BASE_URL=https://...      # 任意 OpenAI 兼容接口
LLM_API_KEY=...
LLM_MODEL=...                 # 默认模型，可被 --model 覆盖
```

## 复现实验
文件命名：`{模型}_[ce_]{初始提示}_{反馈}_r5.jsonl`，`ce_` 表示 ClassEval。支持断点续跑，中断后用同样的命令重跑即可。

```powershell
# 主实验（示例：Doubao，HumanEval，direct 起点，hint 反馈，最多 5 轮）
python src/repair.py --dataset humaneval --model doubao-seed-2-0-mini-260428 --prompt direct --feedback hint --rounds 5 --strip-main -j 6 -o results/exp/doubao_mini_direct_hint_r5.jsonl

# ClassEval：把 --dataset 换成 classeval，输出名加 ce_
python src/repair.py --dataset classeval --model doubao-seed-2-0-mini-260428 --prompt syntax --feedback hint --rounds 5 --strip-main -j 6 -o results/exp/doubao_mini_ce_syntax_hint_r5.jsonl

# 补强 1：只给编译错误（不拼接测试，编译通过即停）
python src/repair.py --model doubao-seed-2-0-mini-260428 --prompt direct --feedback hint --rounds 5 --strip-main --compile-only-feedback -o results/ablation/doubao_mini_direct_hint_compileonly_r5.jsonl

# 补强 2：共享第 0 轮（所有组从同一份第 0 轮代码出发），temperature 0.3，重复 3 次
python src/repair.py --model doubao-seed-2-0-mini-260428 --prompt direct --feedback hint --rounds 5 --strip-main --init results/ablation/doubao_mini_r0_init.jsonl --temperature 0.3 -o results/ablation/doubao_mini_shared_hint_rep1.jsonl

# 补强 3：独立重采样 pass@6
python src/sample_passk.py --model doubao-seed-2-0-mini-260428 --prompt direct -k 6 --temp 0.8 -o results/ablation/doubao_mini_direct_pass6.jsonl

# ClassEval 全部测试复评 → results/reeval/
python src/reeval_classeval.py

# 新协议（第 2 阶段起）：rag 反馈；ClassEval 用全部测试驱动修复（每轮跑全部测试，全部通过才停）
python src/repair.py --model doubao-seed-2-0-mini-260428 --prompt direct --feedback rag --rounds 5 --strip-main -o results/exp/doubao_mini_direct_rag_r5.jsonl
python src/repair.py --dataset classeval --all-tests --model doubao-seed-2-0-mini-260428 --prompt direct --feedback hint --rounds 5 --strip-main -o results/exp/doubao_mini_ce_direct_hint_alltests_r5.jsonl

# 共享第 0 轮：先只生成第 0 轮，再让各反馈组用 --init 读入同一份代码
python src/repair.py --model doubao-seed-2-0-mini-260428 --prompt direct --rounds 0 --strip-main --temperature 0.3 -o results/shared/doubao_mini_direct_r0.jsonl
python src/repair.py --model doubao-seed-2-0-mini-260428 --prompt direct --feedback rag --rounds 5 --strip-main --temperature 0.3 --init results/shared/doubao_mini_direct_r0.jsonl -o results/shared/doubao_mini_direct_rag_rep1.jsonl

# 不调用 API 的流程自检：用官方参考答案作为第 0 轮（ClassEval 全部测试应为 82/84，HumanEval 应为 164/164）
python src/repair.py --dataset classeval --all-tests --init external/CangjieBench/CangjieBench/ClassEval_Cangjie.jsonl --rounds 0 -o results/try/ce_ref_alltests.jsonl

# 新题集 Original-30（30 道新写的题，格式同 HumanEval）：参考答案自检应为 30/30，再按矩阵运行
python src/repair.py --dataset original --prompt direct --init data/original30/Original30_Cangjie.jsonl --rounds 0 -o results/try/or_ref.jsonl
python src/run_matrix.py --matrix original --dry-run

# 第 3 阶段 / 新题集统计 → results/stats/{stage3,original30}_stats.{md,json}
python src/stage3_stats.py
python src/stage3_stats.py --matrix original
# ClassEval 剩余失败与反馈截断检查 → results/stats/residual_failures.{md,json}（--recheck 需要 cjc）
python src/residual_failures.py --recheck -j 6
# 延长修复轮数补充实验（Doubao HumanEval direct，最多 10 轮）→ results/stats/rounds10_stats.{md,json}、results/figures/fig5_rounds10_curve.png
python src/rounds10_stats.py
# 全部实验 token 消耗与美元成本（国际站官网标价，DeepSeek 高峰价）→ results/stats/token_cost_stats.{md,json}
python src/token_cost.py

# 统计、检验、作图、测试
python src/analyze.py
python src/split_eval.py
python src/plot_figures.py
python -m pytest tests
```

## 数据说明
- 原始实验输出（`results/exp`、`results/ablation`、`results/reeval`，以及 `results/stage3`、`results/original30` 的 `r0/`、`runs/` 下的 `*.jsonl`，约 145 MB）不进 git，随项目打包的 zip 一起分发；`*.summary.json` 在 git 中。
- 数字核对：`python src/check_numbers.py <文档>` 检查文档中的差值、置信区间、均值 ± SD、p 值和美元金额能否在 `results/stats/*_stats.json` 中找到。
- 第 2 阶段起，每条记录额外写入 `model`、`temperature_used`（实际温度），summary 写入 `prompt_version`（2 = blind 提示改为同时覆盖编译失败；此前实验为 1）。`LLM_TIMEOUT` 环境变量可调整单次请求超时（默认 240 秒）。
- 模型版本：`deepseek-v4-1-flash-261017`、`doubao-seed-2-0-mini-260428`、`kimi-k3-1-pro-261024`。主实验 temperature 为 0；**Kimi-K3.1-Pro 的 API 只允许 1**，由 `llm.py` 自动回退。各组实际参数见汇总报告第二节。

## 许可证
- 代码（`src/`、`tests/`）：MIT，见 `LICENSE`。
- 数据（`data/original30/`、`results/`、`docs/`）：CC BY 4.0，见 `LICENSE-DATA`。
- `results/` 中来自 CangjieBench 的题目、测试、文档片段和公开模型输出仍按其 MIT 许可证使用，见 `THIRD_PARTY_NOTICES.md`。
