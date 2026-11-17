# 补充统计（零成本，自动生成）

价格快照：火山方舟官网在线推理（常规）单价，2026-11-17；实验实际通过 Coding Plan 订阅调用，下表为等价折算。

## 1. Test 半区（seed=42，N=82）hint vs raw，R5

| 配置 | hint | raw | hint 独过 | raw 独过 | p |
|---|---|---|---|---|---|
| doubao_mini_direct | 46.34% | 39.02% | 13 | 7 | 0.2632 |
| doubao_mini_syntax | 90.24% | 87.80% | 4 | 2 | 0.6875 |
| ds_v41f_direct | 100.00% | 100.00% | 0 | 0 | 1.0000 |
| kimik31p_direct | 100.00% | 100.00% | 0 | 0 | 1.0000 |

共享 R0（3 次重复）Test 半区 hint − raw = +14.63 个百分点，95% CI [7.32, 22.36]

规则在 CangjieBench 公开失败样本中的命中次数：

| 规则 | Dev | Test |
|---|---|---|
| if_while_parens | 1300 | 1366 |
| for_in | 1187 | 1368 |
| range | 164 | 199 |
| let_mut | 82 | 96 |
| lambda | 314 | 238 |
| else_return_braces | 475 | 378 |
| ternary_question | 42 | 80 |
| not_operator | 64 | 76 |
| type_annotation_brackets | 25 | 22 |
| number_suffix | 23 | 32 |
| duplicate_main | 136 | 126 |
| string_char_compare | 109 | 103 |
| string_member | 200 | 119 |
| arraylist_member | 116 | 146 |
| undeclared | 503 | 428 |
| type_mismatch | 303 | 341 |

## 2. 多重比较（R5，McNemar 精确检验）

主比较 doubao_mini_direct_hint_r5 vs doubao_mini_direct_raw_r5：51.22% vs 39.02%，29/9，p = 0.0017（单独检验，α = 0.05）。

其余比较（Holm 校正）：

| 组别 | A | B | A% | B% | A 独过 | B 独过 | p | p (Holm) |
|---|---|---|---|---|---|---|---|---|
| doubao_mini_direct | doubao_mini_direct_hint_r5 | doubao_mini_direct_blind_r5 | 51.22 | 13.41 | 67 | 5 | <0.0001 | <0.0001 |
| doubao_mini_direct | doubao_mini_direct_raw_r5 | doubao_mini_direct_blind_r5 | 39.02 | 13.41 | 47 | 5 | <0.0001 | <0.0001 |
| doubao_mini_syntax | doubao_mini_syntax_hint_r5 | doubao_mini_syntax_raw_r5 | 86.59 | 83.54 | 11 | 6 | 0.3323 | 1.0000 |
| ds_v41f_direct | ds_v41f_direct_hint_r5 | ds_v41f_direct_raw_r5 | 99.39 | 99.39 | 1 | 1 | 1.0000 | 1.0000 |
| ds_v41f_direct | ds_v41f_direct_hint_r5 | ds_v41f_direct_blind_r5 | 99.39 | 95.12 | 8 | 1 | 0.0391 | 0.2734 |
| ds_v41f_direct | ds_v41f_direct_raw_r5 | ds_v41f_direct_blind_r5 | 99.39 | 95.12 | 7 | 0 | 0.0156 | 0.1250 |
| kimik31p_direct | kimik31p_direct_hint_r5 | kimik31p_direct_raw_r5 | 100.00 | 100.00 | 0 | 0 | 1.0000 | 1.0000 |
| doubao_mini_ce_direct | doubao_mini_ce_direct_hint_r5 | doubao_mini_ce_direct_raw_r5 | 11.90 | 13.10 | 6 | 7 | 1.0000 | 1.0000 |
| doubao_mini_ce_direct | doubao_mini_ce_direct_hint_r5 | doubao_mini_ce_direct_blind_r5 | 11.90 | 2.38 | 8 | 0 | 0.0078 | 0.0703 |
| doubao_mini_ce_direct | doubao_mini_ce_direct_raw_r5 | doubao_mini_ce_direct_blind_r5 | 13.10 | 2.38 | 9 | 0 | 0.0039 | 0.0391 |
| doubao_mini_ce_syntax | doubao_mini_ce_syntax_hint_r5 | doubao_mini_ce_syntax_raw_r5 | 25.00 | 27.38 | 4 | 6 | 0.7539 | 1.0000 |
| ds_v41f_ce_direct | ds_v41f_ce_direct_hint_r5 | ds_v41f_ce_direct_raw_r5 | 54.76 | 57.14 | 3 | 5 | 0.7266 | 1.0000 |
| compile_only | doubao_mini_direct_hint_compileonly_r5 | doubao_mini_direct_raw_compileonly_r5 | 50.00 | 32.93 | 37 | 9 | <0.0001 | 0.0005 |
| shared_rep1 | doubao_mini_shared_hint_rep1 | doubao_mini_shared_raw_rep1 | 57.32 | 42.07 | 30 | 5 | <0.0001 | 0.0003 |
| shared_rep2 | doubao_mini_shared_hint_rep2 | doubao_mini_shared_raw_rep2 | 54.88 | 39.02 | 32 | 6 | <0.0001 | 0.0003 |
| shared_rep3 | doubao_mini_shared_hint_rep3 | doubao_mini_shared_raw_rep3 | 54.88 | 42.07 | 31 | 10 | 0.0015 | 0.0160 |

## 3. 成本（元）

DeepSeek 列出高峰价，括号内为空闲价；每题、每个通过题成本按高峰价。

| 实验 | N | 输入 tokens | 输出 tokens | 总成本 | 每题 | 通过数 | 每个通过题 |
|---|---|---|---|---|---|---|---|
| doubao_mini_direct_hint_compileonly_r5 | 164 | 813,783 | 954,847 | 2.07 | 0.0126 | 82 | 0.0253 |
| doubao_mini_direct_pass6 | 164 | 261,696 | 2,389,446 | 4.83 | 0.0295 | 28 | 0.1725 |
| doubao_mini_direct_raw_compileonly_r5 | 164 | 874,678 | 1,105,842 | 2.39 | 0.0146 | 54 | 0.0442 |
| doubao_mini_shared_hint_rep1 | 164 | 846,171 | 635,765 | 1.44 | 0.0088 | 94 | 0.0153 |
| doubao_mini_shared_hint_rep2 | 164 | 835,818 | 645,287 | 1.46 | 0.0089 | 90 | 0.0162 |
| doubao_mini_shared_hint_rep3 | 164 | 856,761 | 646,699 | 1.47 | 0.0089 | 90 | 0.0163 |
| doubao_mini_shared_raw_rep1 | 164 | 829,233 | 744,129 | 1.65 | 0.0101 | 69 | 0.0240 |
| doubao_mini_shared_raw_rep2 | 164 | 830,101 | 743,988 | 1.65 | 0.0101 | 64 | 0.0258 |
| doubao_mini_shared_raw_rep3 | 164 | 821,104 | 739,696 | 1.64 | 0.0100 | 69 | 0.0238 |
| doubao_mini_ce_direct_blind_r5 | 84 | 1,572,229 | 1,779,332 | 3.87 | 0.0461 | 2 | 1.9365 |
| doubao_mini_ce_direct_hint_r5 | 84 | 1,923,949 | 1,110,648 | 2.61 | 0.0310 | 10 | 0.2606 |
| doubao_mini_ce_direct_raw_r5 | 84 | 1,798,413 | 1,068,796 | 2.50 | 0.0297 | 11 | 0.2270 |
| doubao_mini_ce_syntax_hint_r5 | 84 | 2,389,827 | 1,100,445 | 2.68 | 0.0319 | 21 | 0.1276 |
| doubao_mini_ce_syntax_raw_r5 | 84 | 2,218,506 | 1,069,770 | 2.58 | 0.0308 | 23 | 0.1123 |
| doubao_mini_direct_blind_r5 | 164 | 697,410 | 2,192,627 | 4.53 | 0.0276 | 22 | 0.2057 |
| doubao_mini_direct_hint_r5 | 164 | 924,658 | 1,049,545 | 2.28 | 0.0139 | 84 | 0.0272 |
| doubao_mini_direct_raw_r5 | 164 | 891,958 | 1,183,183 | 2.54 | 0.0155 | 64 | 0.0398 |
| doubao_mini_syntax_hint_r5 | 164 | 1,369,565 | 795,650 | 1.86 | 0.0114 | 142 | 0.0131 |
| doubao_mini_syntax_raw_r5 | 164 | 1,450,044 | 831,582 | 1.95 | 0.0119 | 137 | 0.0143 |
| ds_v41f_ce_direct_hint_r5 | 84 | 357,655 | 1,477,385 | 12.53 (6.27) | 0.1492 | 46 | 0.2725 |
| ds_v41f_ce_direct_raw_r5 | 84 | 391,685 | 1,878,247 | 15.81 (7.91) | 0.1882 | 48 | 0.3294 |
| ds_v41f_direct_blind_r5 | 164 | 141,324 | 1,368,850 | 11.23 (5.62) | 0.0685 | 156 | 0.0720 |
| ds_v41f_direct_hint_r5 | 164 | 102,822 | 954,535 | 7.84 (3.92) | 0.0478 | 163 | 0.0481 |
| ds_v41f_direct_raw_r5 | 164 | 101,009 | 1,005,033 | 8.24 (4.12) | 0.0503 | 163 | 0.0506 |
| ds_v41f_syntax_hint_r5 | 164 | 445,297 | 384,751 | 3.97 (1.98) | 0.0242 | 164 | 0.0242 |
| kimik31p_direct_hint_r5 | 164 | 84,823 | 389,463 | 27.59 | 0.1682 | 164 | 0.1682 |
| kimik31p_direct_raw_r5 | 164 | 89,867 | 406,754 | 28.83 | 0.1758 | 164 | 0.1758 |

合计（DeepSeek 按高峰价）：162.1 元

token-通过率曲线（Doubao，HumanEval，direct；修复组按每题调用次数平均分摊 token，为近似值）：

- pass@k: 0.44M→6.8%, 0.88M→9.9%, 1.33M→12.2%, 1.77M→14.0%, 2.21M→15.6%, 2.65M→17.1%
- doubao_mini_direct_blind_r5: 0.52M→7.9%, 1.00M→9.8%, 1.48M→11.0%, 1.96M→12.8%, 2.42M→12.8%, 2.89M→13.4%
- doubao_mini_direct_raw_r5: 0.41M→9.2%, 0.78M→17.1%, 1.14M→25.0%, 1.47M→31.7%, 1.78M→34.8%, 2.08M→39.0%
- doubao_mini_direct_hint_r5: 0.41M→9.8%, 0.78M→25.0%, 1.12M→32.9%, 1.42M→39.0%, 1.71M→45.1%, 1.97M→51.2%
- doubao_mini_direct_hint_compileonly_r5: 0.39M→8.5%, 0.76M→18.3%, 1.07M→28.7%, 1.35M→41.5%, 1.57M→46.3%, 1.77M→50.0%
- doubao_mini_direct_raw_compileonly_r5: 0.40M→9.2%, 0.76M→17.1%, 1.08M→19.5%, 1.40M→25.0%, 1.70M→28.7%, 1.98M→32.9%

## 4. 口径

第 0 轮失败类型分布（timeout 包含编译超时与运行超时）：

- doubao_mini_ce_direct_blind_r5: {'compile_error': 82, 'passed': 2}
- doubao_mini_ce_direct_hint_r5: {'compile_error': 81, 'passed': 3}
- doubao_mini_ce_direct_raw_r5: {'compile_error': 81, 'passed': 3}
- doubao_mini_ce_syntax_hint_r5: {'compile_error': 74, 'passed': 8, 'runtime_exception': 1, 'test_failure': 1}
- doubao_mini_ce_syntax_raw_r5: {'compile_error': 73, 'passed': 9, 'runtime_exception': 1, 'timeout': 1}
- doubao_mini_direct_blind_r5: {'compile_error': 147, 'passed': 13, 'timeout': 1, 'test_failure': 3}
- doubao_mini_direct_hint_compileonly_r5: {'compile_error': 147, 'passed': 14, 'test_failure': 3}
- doubao_mini_direct_hint_r5: {'compile_error': 147, 'passed': 16, 'test_failure': 1}
- doubao_mini_direct_raw_compileonly_r5: {'compile_error': 146, 'passed': 15, 'test_failure': 3}
- doubao_mini_direct_raw_r5: {'compile_error': 147, 'passed': 15, 'test_failure': 2}
- doubao_mini_shared_hint_rep1: {'compile_error': 147, 'passed': 16, 'test_failure': 1}
- doubao_mini_shared_hint_rep2: {'compile_error': 147, 'passed': 16, 'test_failure': 1}
- doubao_mini_shared_hint_rep3: {'compile_error': 147, 'passed': 16, 'test_failure': 1}
- doubao_mini_shared_raw_rep1: {'compile_error': 147, 'passed': 16, 'test_failure': 1}
- doubao_mini_shared_raw_rep2: {'compile_error': 147, 'passed': 16, 'test_failure': 1}
- doubao_mini_shared_raw_rep3: {'compile_error': 147, 'passed': 16, 'test_failure': 1}
- doubao_mini_syntax_hint_r5: {'passed': 73, 'compile_error': 81, 'test_failure': 8, 'runtime_exception': 2}
- doubao_mini_syntax_raw_r5: {'compile_error': 81, 'passed': 76, 'test_failure': 7}
- ds_v41f_ce_direct_hint_r5: {'compile_error': 44, 'passed': 37, 'test_failure': 3}
- ds_v41f_ce_direct_raw_r5: {'compile_error': 46, 'passed': 31, 'test_failure': 6, 'runtime_exception': 1}
- ds_v41f_direct_blind_r5: {'passed': 121, 'compile_error': 41, 'test_failure': 2}
- ds_v41f_direct_hint_r5: {'passed': 112, 'compile_error': 45, 'test_failure': 5, 'runtime_exception': 2}
- ds_v41f_direct_raw_r5: {'passed': 117, 'compile_error': 43, 'runtime_exception': 1, 'test_failure': 3}
- ds_v41f_syntax_hint_r5: {'passed': 153, 'compile_error': 11}
- kimik31p_direct_hint_r5: {'passed': 133, 'compile_error': 30, 'test_failure': 1}
- kimik31p_direct_raw_r5: {'passed': 120, 'compile_error': 41, 'test_failure': 3}

反馈截断（只统计 raw / hint，blind 不发送报错）：

| 实验 | 发送的反馈数 | 存储达上限 1500 | 超过 3000（被截断） | 未核实 |
|---|---|---|---|---|
| doubao_mini_ce_direct_hint_r5 | 374 | 76 | 2 | 0 |
| doubao_mini_ce_direct_raw_r5 | 379 | 86 | 2 | 0 |
| doubao_mini_ce_syntax_hint_r5 | 310 | 52 | 1 | 0 |
| doubao_mini_ce_syntax_raw_r5 | 298 | 38 | 1 | 0 |
| doubao_mini_direct_hint_compileonly_r5 | 524 | 7 | 0 | 0 |
| doubao_mini_direct_hint_r5 | 571 | 11 | 0 | 0 |
| doubao_mini_direct_raw_compileonly_r5 | 600 | 11 | 2 | 0 |
| doubao_mini_direct_raw_r5 | 627 | 19 | 0 | 0 |
| doubao_mini_shared_hint_rep1 | 560 | 12 | 0 | 0 |
| doubao_mini_shared_hint_rep2 | 555 | 12 | 0 | 0 |
| doubao_mini_shared_hint_rep3 | 563 | 9 | 0 | 0 |
| doubao_mini_shared_raw_rep1 | 608 | 13 | 0 | 0 |
| doubao_mini_shared_raw_rep2 | 613 | 15 | 0 | 0 |
| doubao_mini_shared_raw_rep3 | 606 | 19 | 0 | 0 |
| doubao_mini_syntax_hint_r5 | 243 | 6 | 0 | 0 |
| doubao_mini_syntax_raw_r5 | 272 | 6 | 0 | 0 |
| ds_v41f_ce_direct_hint_r5 | 96 | 17 | 0 | 0 |
| ds_v41f_ce_direct_raw_r5 | 101 | 22 | 0 | 0 |
| ds_v41f_direct_hint_r5 | 68 | 3 | 0 | 0 |
| ds_v41f_direct_raw_r5 | 70 | 2 | 0 | 0 |
| ds_v41f_syntax_hint_r5 | 13 | 1 | 0 | 0 |
| kimik31p_direct_hint_r5 | 33 | 0 | 0 | 0 |
| kimik31p_direct_raw_r5 | 50 | 0 | 0 | 0 |
