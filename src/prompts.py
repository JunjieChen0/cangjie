"""提示词模板。

- direct / syntax：复现 CangjieBench 的两种基线（模板来自其 Prompts/ 目录）
- repair_*：本项目的核心——不同形式的"编译器反馈"修复提示（消融实验的自变量）
"""
from __future__ import annotations

SYSTEM = "You are an expert Cangjie (仓颉) programmer."

DIRECT = """Please complete the following Cangjie function. Write the complete code and wrap it in ```cangjie```.
Do NOT write a main() function.

{question}
"""

SYNTAX = """You are an expert assistant for the Cangjie programming language. Please answer questions based on the **syntax rules** provided by the user.

1. Prioritize explicit rules in the syntax rules.
2. Reasonable inference only when necessary.
3. Import necessary packages at the top of the program if required.
4. Do NOT write a main() function.

Write the complete code and wrap it in ```cangjie```.

## Syntax Rules

{syntax_rule}

## Question

{question}
"""

# ---------- 修复提示：三种反馈粒度 ----------

# 提示词版本：1 = 2026-11-17 之前的全部实验；2 = blind 措辞改为同时覆盖编译失败（纯编译反馈消融中并未运行测试）
PROMPT_VERSION = 2

# R0: 只告诉"错了"，不给任何信息（对照组，检验"多试几次"本身的效果）
REPAIR_BLIND = """Your previous Cangjie code did not compile or did not pass the tests. Please fix it.
Return the complete corrected code in ```cangjie```. Do NOT write a main() function.
"""

# R1: 原始编译器 / 运行时报错
REPAIR_RAW = """Your previous Cangjie code failed ({kind}). Here is the error output:

```
{feedback}
```

Please fix the code. Return the complete corrected code in ```cangjie```. Do NOT write a main() function.
"""

# R2: 原始报错 + 针对错误类型的修复提示（hints 由 repair_hints.py 根据报错规则匹配得到）
REPAIR_HINT = """Your previous Cangjie code failed ({kind}). Here is the error output:

```
{feedback}
```

Hints about Cangjie that are likely relevant to this error:
{hints}

Please fix the code. Return the complete corrected code in ```cangjie```. Do NOT write a main() function.
"""

# R3: 原始报错 + 用报错文本从官方文档检索到的片段（doc_retrieval.py，BM25），与 hint 结构一致
REPAIR_RAG = """Your previous Cangjie code failed ({kind}). Here is the error output:

```
{feedback}
```

Excerpts from the official Cangjie documentation that may be relevant to this error:
{docs}

Please fix the code. Return the complete corrected code in ```cangjie```. Do NOT write a main() function.
"""
