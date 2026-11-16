"""根据编译器报错，用规则匹配出"仓颉特有"的修复提示。

这些规则来自 mine_errors.py 对 CangjieBench 公开失败样本（6647 个）的统计，
覆盖了 Top-40 高频 cjc 报错中的大部分。这是本项目可以持续扩充的"错误→知识"库：
  1. 跑实验，收集真实的 cjc 报错
  2. python src/mine_errors.py 统计高频报错模板
  3. 针对高频模板写规则：正则 + 一段简短的仓颉正确写法
规则写得越准，R2(hint) 相比 R1(raw) 的提升越大——这本身就是论文里可以分析的一点。

⚠ 每条提示都要对照官方文档 (https://cangjie-lang.cn) 和 cjc 1.0.x 实测核对后再用于正式实验！
"""
from __future__ import annotations

import re

# (名称, 匹配报错文本的正则, 提示内容)
RULES: list[tuple[str, str, str]] = [
    # --- 外来语法（占失败的大头） ---
    ("if_while_parens",
     r"expected '\(' after '(if|while)'|expected '\(', found",
     "Conditions MUST be in parentheses: `if (x > 0) { ... }`, `while (i < n) { ... }`. "
     "`if` is an expression; braces are always required."),
    ("for_in",
     r"for-in expression|expected '\(', found|expected pattern, found keyword '(var|let)'",
     "Loop syntax is `for (x in xs) { ... }`, `for (i in 0..n) { ... }`, `for ((i, x) in enumerate(...))` is NOT available; "
     "do not write `for var`/`for let`, no C-style `for (;;)`."),
    ("range",
     r"expected expression after '\.\.'|\.\.<",
     "Ranges: `0..n` is exclusive, `0..=n` is inclusive, step with `0..n : 2`. There is no `..<` operator."),
    ("let_mut",
     r"after 'let', found keyword 'mut'|cannot assign to immutable",
     "Use `var` for mutable variables and `let` for immutable ones; there is no `let mut`. "
     "Function parameters are immutable — copy into a `var` before modifying."),
    ("lambda",
     r"lambda expression|trailing closure|expected ';' or '<NL>', found '=>'",
     "Lambda syntax: `{ a: Int64, b: Int64 => a + b }` or `{ x => x * 2 }` when the type is inferable. "
     "Trailing closure: `list.forEach { x => println(x) }` only after a named function/method call."),
    ("else_return_braces",
     r"found keyword 'else'|expected '\{', found keyword '(return|if)'",
     "Every `if`/`else` branch needs braces: `if (c) { return 1 } else { return 2 }`. `else if` is fine."),
    ("ternary_question",
     r"after '\?'|found '\?'",
     "Cangjie has NO `a ? b : c` ternary. Use `if (cond) { a } else { b }` as an expression. "
     "`?` is only for Option types (e.g. `Option<Int64>` / `?Int64`)."),
    ("not_operator",
     r"found '!'",
     "Logical not is `!cond`, and it must be inside parentheses of `if`: `if (!found) { ... }`."),
    ("type_annotation_brackets",
     r"expected type name after ':', found '\['",
     "Array types are written `Array<Int64>` / `ArrayList<Int64>`, not `[Int64]` or `Int64[]`."),
    ("number_suffix",
     r"unknown suffix .* for number literal",
     "Numeric literal suffixes are like `1i64`, `2u8`, `3.0f64`; `1L`, `2f`, `3.0d` are invalid."),
    # --- 重复 main ---
    ("duplicate_main",
     r"multiple 'main's|function 'main' has overload conflicts",
     "Do NOT define `main()`. The test harness already provides it."),
    # --- API / 类型 ---
    ("string_char_compare",
     r"on type '(UInt8|Rune)' and 'Struct-String'",
     "Character literals are written `r'a'` (type Rune); `'a'` and \"a\" are both String. "
     "`s[i]` returns a UInt8 byte; compare with `b'a'`. Iterate chars with `for (c in s.runes())` or `s.toRuneArray()`."),
    ("string_member",
     r"is not a member of struct 'String'",
     "String has no Python/Java-style helpers like `substring`, `charAt`, `length`. "
     "Use `s.size`, slicing `s[a..b]`, `s.split(\",\")`, `s.contains(...)`, `s.startsWith(...)`, `s.toRuneArray()`, "
     "`s.toAsciiUpper()`/`s.toAsciiLower()`, `s.trimAscii()`."),
    ("arraylist_member",
     r"is not a member of class 'ArrayList",
     # 已用 cjc 1.0.5 实测：1.0 版本中 append/insert 已改名为 add
     "ArrayList API (Cangjie 1.0): `list.size`, `list.add(x)`, `list.add(x, at: i)`, `list.remove(at: i)`, `list[i]`, "
     "`list.clear()`, `list.toArray()`; there is no `append`, `insert`, `push`, `length`, `len()`. "
     "Sorting: `import std.sort.*` then `sort(arr)` (sorts an Array in place)."),
    ("undeclared",
     r"undeclared (identifier|type name)|can not find package",
     "This identifier/package does not exist in Cangjie. Do not invent APIs from other languages. "
     "Common imports: `import std.collection.*`, `import std.math.*`, `import std.sort.*`, `import std.convert.*`."),
    ("type_mismatch",
     r"mismatched types|type incompatible|no matching function for operator",
     "No implicit numeric conversion: use `Float64(x)`, `Int64(y)`. Integer literals are Int64 by default. "
     "Calling an object like a function `x()` is invalid unless it is a function type."),
]


def match_hints(feedback: str, max_hints: int = 3) -> list[str]:
    hits = []
    for name, pattern, hint in RULES:
        if re.search(pattern, feedback, re.I):
            hits.append(f"- [{name}] {hint}")
        if len(hits) >= max_hints:
            break
    return hits or ["- (no specific hint matched) Read the error carefully and follow Cangjie syntax."]
