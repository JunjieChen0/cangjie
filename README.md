# 仓颉代码生成：低成本编译反馈修复研究

> 工作题目：**《面向低资源语言仓颉的轻量级编译反馈修复：用几轮对话逼近 Agent 的效果？》**

## 一句话
CangjieBench（ESEM 2026）发现：语法约束提示一次生成能做到 40–64% 的通过率，GPT-5 + Codex Agent 能做到 85%，但 token 消耗极高；用便宜模型的 Agent 只有 25–39%。
**本项目研究中间地带**：不使用 Agent 框架，只做"生成 → cjc 编译 → 把报错喂回去"的几轮循环，
回答**哪种反馈最有用、几轮够用、花多少钱**这几个问题。

## 目录
```
src/
  runner.py        本地 cjc 编译运行 + 判定（与 CangjieBench 官方判定一致，已验证）
  data.py          加载 CangjieBench HumanEval（164 题）
  evaluate.py      评测 solutions jsonl
  llm.py           OpenAI 兼容 API 调用（DeepSeek/Qwen/GLM/Kimi/Ollama 都行）
  prompts.py       提示词：基线 + 三种修复反馈（blind / raw / hint）
  repair_hints.py  "报错 → 仓颉知识"规则库（数据驱动，需要持续核对扩充）
  repair.py        核心实验：生成 + 多轮修复
  mine_errors.py   从公开失败样本中统计高频 cjc 报错（零成本）
  postprocess.py   零成本后处理实验
external/CangjieBench/   数据集与公开结果（MIT 许可，git clone 而来）
results/                 实验输出
docs/研究计划.md          研究问题、实验设计、分工、时间表
```

## 快速开始
```powershell
pip install -r requirements.txt

# 1. 环境自检：官方参考答案应 164/164 通过（已验证 ✅）
python src/evaluate.py --reference

# 2. 复现论文数字：DeepSeek-V3 语法约束（论文 40.9%，本地 40.85% ✅）
python src/evaluate.py -i external/CangjieBench/Results/Text_to_Code/Syntax_Constrained/DeepSeek-V3_HumanEval.jsonl -o results/repro/ds_v3_syntax.records.jsonl

# 3. 高频报错统计（零成本）
python src/mine_errors.py

# 4. 配置大模型 API（以 DeepSeek 为例；也可以用硅基流动等平台的免费模型，或本地 Ollama）
$env:LLM_BASE_URL="https://api.deepseek.com/v1"
$env:LLM_API_KEY="sk-..."
$env:LLM_MODEL="deepseek-chat"

# 5. 小规模试跑（10 题，3 轮 raw 反馈）
python src/repair.py --prompt syntax --feedback raw --rounds 3 --limit 10 -o results/try/ds_syntax_raw.jsonl

# 6. 省钱技巧：直接从 CangjieBench 公开的第 0 轮结果开始修复，第 0 轮不花钱
python src/repair.py --init external/CangjieBench/Results/Text_to_Code/Syntax_Constrained/DeepSeek-V3_HumanEval.jsonl `
    --prompt syntax --feedback hint --rounds 3 -o results/exp/ds_init_hint_r3.jsonl
```
