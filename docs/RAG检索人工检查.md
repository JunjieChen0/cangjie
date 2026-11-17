# RAG 检索人工检查（第 2 阶段，实验前）

- 日期：2026-11-17；检索器：`src/doc_retrieval.py`（BM25，TOP_K = 3，MAX_CHARS = 2000，参数在任何 rag 实验之前固定）
- 样本：从 `doubao_mini_direct_raw_r5`（HumanEval）与 `doubao_mini_ce_direct_raw_r5`（ClassEval）的修复反馈中，按 `analyze.classify_error` 类别随机抽取 10 条（随机种子 7）
- 判定：top-3 中是否有能直接指导修复的文档片段（✓ 相关 / ~ 部分相关 / ✗ 不相关）

| # | 类别 | 报错（节选） | 需要的知识 | top-3 检索结果（节选） | 判定 |
|---|---|---|---|---|---|
| 1 | 外来语法 | `unclosed delimiter: '('`，源码 `for (i in 0 until lst.size())` | 区间写法 `0..n` | String.join、ConcurrentHashMap 示例、抽象属性 | ✗ |
| 2 | 外来语法 | `found 'primeHexDigits'`，源码 `val primeHexDigits = Set{...}` | `let`/`var`，HashSet 构造 | Decimal.init、**HashSet**、排序示例 | ~ |
| 3 | 外来语法 | `found 'tokens'`，源码 `val tokens = ....split(Regex(...))` | `let`/`var`，字符串切分 | **regex 示例**、**String.lazySplit**、Regex 用法 | ~ |
| 4 | 外来语法 | `expected '=>' in lambda expression, found keyword 'this'` | 构造函数 / lambda 语法 | ast 包 DoWhileExpr、ForInExpr、MatchCase | ✗ |
| 5 | API/标识符 | `undeclared identifier 'abs'` | `import std.math.abs` | 属性修饰符、泛型结构体、调用函数 | ✗ |
| 6 | API/标识符 | `'append' is not a member of class 'ArrayList<Int64>'` | `ArrayList.add` | **ArrayList 的 add 函数**、remove/clear、ArrayList | ✓ |
| 7 | API/标识符 | `'containsKey' is not a member of class 'HashMap<...>'` | `HashMap.contains` | **访问 HashMap 成员**、**HashMap.contains(K)**、get/add/contains 示例 | ✓ |
| 8 | 类型 | `invalid binary operator '>' on type 'Float64' and 'Int64'` | 数值类型需显式转换 | 关键字、TokenKind、**浮点类型字面量** | ~ |
| 9 | 类型 | `invalid binary operator '+' on type 'Option<Int64>' ...` | `get()` 返回 Option，需解包 | ConcurrentHashMapIterator.next、Future.tryGet、ArrayIterator.next | ✗ |
| 10 | 类型 | `invalid binary operator '-' on type 'Float64' and 'Option<Float64>'` | 同上 | MaxMinValue、clamp、**Float64** | ~ |

**汇总**：相关 2 条，部分相关 4 条，不相关 4 条。

**观察**

1. **API 类错误检索效果好**：报错里带有类名、方法名（`ArrayList`、`HashMap`、`containsKey`），能和 API 文档的标识符直接匹配上。
2. **外来语法错误检索不到**：报错里的 `val`、`until`、`0..<` 这类写法来自其他语言，官方文档只讲仓颉的正确写法，不会提到这些写法，所以无从匹配。这正好是 `repair_hints.py` 规则库覆盖的错误类型，说明人工整理的"外来写法 → 仓颉写法"知识，在文档检索里补不回来。
3. **类型错误只有部分相关**：能检索到涉及的类型，但检索不到"需要显式转换""Option 需要解包"这类具体修复方法。

**对实验设计的影响**：BM25 是一个朴素但合理的 RAG 基线。审稿人可能认为它太弱，可以在第 3 阶段加一个向量检索版本作为对照（例如方舟 doubao-embedding，需要按量计费的 API Key）。是否加入由作者决定；如果加入，必须在跑实验前固定好参数。
