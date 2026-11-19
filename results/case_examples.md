# 典型修复案例素材（自动挑选）

数据：第 3 阶段 Doubao-Seed-2.0-mini，`direct` 起点，共享第 0 轮，3 次重复。

## 案例 1：hint 修复外来语法：HumanEval 第 154 题

挑选规则：第 0 轮 foreign_syntax 且匹配到具体规则；raw 3/3 失败，hint 3/3 通过；diff 最短

raw 3 次重复的最终结果：compile_error, compile_error, compile_error；该组第 1 次重复第 2 轮通过。

第 0 轮报错（节选）：
```
error: expected '(' after 'if', found 'lenB'
 ==> main.cj:4:8:
  | 
4 |     if lenB > lenA {
  |     ~~ ^^^^ expected '(' here
  |     |
  |     after this
  | 

error: expected expression after '..', found '<'
 ==> main.cj:8:18:
  | 
8 |     for (i in 0..<lenB) {
  |                  ^ expected expression here
  | 

error: expected '(' after 'if', found 'a'
  ==> main.cj:10:12:
   | 
10 |         if a.contains(rotation) {
   |         ~~ ^ expected '(' here
   |         |
   |         after this
   | 

3 errors generated, 3 errors printed.
```

hint 附加给模型的规则提示：
```
- [if_while_parens] Conditions MUST be in parentheses: `if (x > 0) { ... }`, `while (i < n) { ... }`. `if` is an expression; braces are always required.
- [range] Ranges: `0..n` is exclusive, `0..=n` is inclusive, step with `0..n : 2`. There is no `..<` operator.
```

修复前后代码 diff（该组第 1 次重复）：
```diff
--- round 0
+++ repaired
@@ -1,5 +1,5 @@
 func cycpattern_check(a: String, b: String): Bool {
-    let lenA = a.length()
-    let lenB = b.length()
-    if lenB > lenA {
+    let lenA = a.size
+    let lenB = b.size
+    if (lenB > lenA) {
         return false
@@ -7,5 +7,5 @@
     let doubledB = b + b
-    for (i in 0..<lenB) {
-        let rotation = doubledB.substring(i, i + lenB)
-        if a.contains(rotation) {
+    for (i in 0..lenB) {
+        let rotation = doubledB[i..(i + lenB)]
+        if (a.contains(rotation)) {
             return true
```

## 案例 2：rag 修复 API / 未声明标识符：ClassEval 第 72 题

挑选规则：第 0 轮 api_or_undeclared；raw 3/3 失败，rag 3/3 通过；diff 最短

raw 3 次重复的最终结果：compile_error, compile_error, compile_error；该组第 1 次重复第 2 轮通过。

第 0 轮报错（节选）：
```
error: 'isMatch' is not a member of class 'Regex'
 ==> main.cj:8:22:
  | 
8 |         return regex.isMatch(text)
  |                      ^^^^^^^ 
  | 

error: mismatched types
  ==> main.cj:13:16:
   | 
13 |         return regex.findAll(text)
   |                ^^^^^^^^^^^^^^^^^^^ expected 'Class-ArrayList<Struct-String>', found 'Struct-Array<Struct-MatchData>'
   | 

error: mismatched types
  ==> main.cj:18:16:
   | 
18 |         return regex.split(text)
   |                ^^^^^^^^^^^^^^^^^ expected 'Class-ArrayList<Struct-String>', found 'Struct-Array<Struct-String>'
   | 

error: mismatched types
  ==> main.cj:41:16:
   | 
41 |         return regex.split(text)
   |                ^^^^^^^^^^^^^^^^^ expected 'Class-ArrayList<Struct-String>', found 'Struct-Array<Struct-String>'
   | 

4
```

rag 检索到的文档片段（标题）：
```
libs/std/regex/regex_package_api/regex_package_classes.md > 类 > class Regex > func findAll(String, Bool)
libs/std/regex/regex_samples/regex_sample.md > regex 示例 > Regex 和 MatchData 的使用
libs/std/regex/regex_samples/regex_sample.md > regex 示例 > Regex 匹配多行
```

修复前后代码 diff（该组第 1 次重复）：
```diff
--- round 0
+++ repaired
@@ -2,2 +2,3 @@
 import std.collection.ArrayList
+import std.regex.MatchData
 
@@ -7,3 +8,4 @@
         let regex = Regex(pattern)
-        return regex.isMatch(text)
+        let matches = regex.findAll(text)
+        return matches.size > 0
     }
@@ -12,3 +14,8 @@
         let regex = Regex(pattern)
-        return regex.findAll(text)
+        let matches = regex.findAll(text)
+        let result = ArrayList<String>()
+        for (md in matches) {
+            result.add(md.matchString())
+        }
+        return result
     }
@@ -17,3 +24,8 @@
         let regex = Regex(pattern)
-        return regex.split(text)
+        let splitArr = regex.split(text)
+        let result = ArrayList<String>()
+        for (s in splitArr) {
+            result.add(s)
+        }
+        return result
     }
@@ -40,3 +52,8 @@
         let regex = Regex(pattern)
-        return regex.split(text)
+        let splitArr = regex.split(text)
+        let result = ArrayList<String>()
+        for (s in splitArr) {
+            result.add(s)
+        }
+        return result
     }
```

## 案例 3：规格歧义导致的残余失败（ClassEval 第 53 题）

题面原文（含 case 的行）：
```
Words are strictly case sensitive.
```

参考实现在匹配前先把句子转成小写；测试 `test_find_longest_word_4` 要求 "Apple is red." 匹配到 "apple"。
DeepSeek direct raw 第 1 次重复的末轮反馈（修复反馈只给出失败的测试函数名）：
```
1 of 2 tests failed.

[test #1 test_failure]
An exception has occurred:
Exception: Test failed!
	 at default.test_find_longest_word_4()
	 at default.main()
```
