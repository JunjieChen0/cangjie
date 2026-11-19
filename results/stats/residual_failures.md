# ClassEval 剩余失败与反馈截断检查（自动生成）

数据：`results/stage3/runs/` 中 ClassEval 各组（全部测试驱动修复）。题次 = 题 × 重复。

## 修复 5 轮后仍失败的题次

| 模型 | 起点 | 反馈 | 重复 | 失败题次 | 测试失败 | 其中只差一个测试 | API 超时 | 编译/其他 | 每次都失败的题数 |
|---|---|---|---|---|---|---|---|---|---|
| ds_v41f | direct | blind | 3 | 144 | 41 | 14（34%） | 0 | 103 | 40 |
| ds_v41f | direct | hint | 3 | 77 | 66 | 48（73%） | 0 | 11 | 20 |
| ds_v41f | direct | rag | 3 | 70 | 63 | 48（76%） | 0 | 7 | 17 |
| ds_v41f | direct | raw | 3 | 80 | 64 | 44（69%） | 0 | 16 | 19 |
| kimik31p | direct | hint | 1 | 18 | 8 | 8（100%） | 7 | 3 | 18 |
| kimik31p | direct | raw | 1 | 15 | 3 | 2（67%） | 11 | 1 | 15 |

编译/其他 包括 api_or_undeclared、foreign_syntax、type_or_mutability、runtime_exception 等，完整分布见 json 中的 cats。

## 固定难题：raw / hint / rag 每次重复都失败的题（`direct` 起点）

“人工归类”取自 `results\stats\hard_problem_coding.csv`（逐题依据见该文件 evidence 列；coder / reviewer 列记录编码人与复核人）。修复反馈只给出失败的测试函数名，不给断言内容与期望值。
两个模型的清单重叠时，归类以 DeepSeek 的失败为准；仅 Kimi 失败的题按 Kimi 轨迹归类。例如 67 号：DeepSeek 未实现题面要求的跨方法 count 更新，Kimi 则更早失败于编译错误 `undeclared type name 'Dish'`，Kimi 表中该题的归类不表示它未实现扣减库存。

### ds_v41f（16 题）

归类计数：规格歧义：功能行为未说明 8；规格歧义：边界或非法输入约定 3；题意理解：翻译约定 1；仓颉语义：整数溢出 1；基准缺陷：测试不可执行 1；基准缺陷：题面与参考实现矛盾 1；题意理解：跨方法状态依赖 1

| 题号 | 类名 | 最终失败类别 | 测试通过情况（第一条非超时记录） | 反馈开头 | 人工归类 |
|---|---|---|---|---|---|
| 0 | AccessGatewayFilter | foreign_syntax, test_failure | ✗✗✗✗ | error: expected '=>' in lambda expression, found 'set_current_user_info_and_log' ==> main.cj:31:17: \| 31 \| set_current_user_info_and_log(user) \| ^^^^^^^^^^^^^^^ | 规格歧义：功能行为未说明 |
| 4 | Student | test_failure | ✓✓✓✓✗✓✓ | 1 of 7 tests failed. [test #4 test_failure] An exception has occurred: Exception: Test failed! at default.test_get_course_average_1() at default.main() | 题意理解：翻译约定 |
| 16 | Calculator | api_or_undeclared, test_failure | ✗✓✓✓ | 1 of 4 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_calculate_8() at default.main() | 规格歧义：功能行为未说明 |
| 17 | Event | test_failure | ✓✓✓✓✗✓✓ | 1 of 7 tests failed. [test #4 test_failure] An exception has occurred: Exception: Test failed! at default.test_get_available_slots_2() at default.main() | 规格歧义：功能行为未说明 |
| 23 | CombinationCalculator | api_or_undeclared, runtime_exception, test_failure | ✗✗✗✗✗✗ | error: undeclared identifier 'toInt64' ==> main.cj:84:18: \| 84 \| return v.toInt64() \| ^^^^^^^ \| 1 error generated, 1 error printed. | 仓颉语义：整数溢出 |
| 36 | EmailClient | api_or_undeclared, other_compile, test_failure | ✗✗✗✗✗✗ | error: 'isNone' is not a member of interface 'Any' ==> main.cj:59:35: \| 59 \| if (email["time"].isNone()) { \| ^^^^^^ \| error: invalid binary operator '<' on type | 规格歧义：功能行为未说明 |
| 39 | ExpressionCalculator | api_or_undeclared, test_failure | ✗✗✓✗✓✗✗ | 5 of 7 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_calculate_1() at default.main() 53485150525151504 | 规格歧义：功能行为未说明 |
| 43 | Employee | foreign_syntax, test_failure, type_or_mutability | ✓✓✗✓✓✓ | 1 of 6 tests failed. [test #2 test_failure] An exception has occurred: Exception: Test failed! at default.test_update_employee_6() at default.main() | 规格歧义：功能行为未说明 |
| 48 | IpUtil | api_or_undeclared, foreign_syntax, test_failure | ✓✓✗✗ | 2 of 4 tests failed. [test #2 test_failure] An exception has occurred: Exception: Test failed! at default.test_get_hostname_1() at default.main() [test #3 test_ | 基准缺陷：测试不可执行 |
| 53 | LongestWord | api_or_undeclared, test_failure | ✓✗ | 1 of 2 tests failed. [test #1 test_failure] An exception has occurred: Exception: Test failed! at default.test_find_longest_word_4() at default.main() | 基准缺陷：题面与参考实现矛盾 |
| 57 | MetricsCalculator2 | api_or_undeclared, foreign_syntax, test_failure | ✗✗✓ | 2 of 3 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_mrr_7() at default.main() [test #1 test_failure]  | 规格歧义：边界或非法输入约定 |
| 61 | MusicPlayer | test_failure | ✓✓✗✓✓✓✓✓✓ | 1 of 9 tests failed. [test #2 test_failure] An exception has occurred: Exception: Test failed! at default.test_play_4() at default.main() | 规格歧义：功能行为未说明 |
| 65 | NumberWordFormatter | test_failure | ✗✗✓✓✓✓ | 2 of 6 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_format_4() at default.main() [test #1 test_failur | 规格歧义：功能行为未说明 |
| 66 | NumericEntityUnescaper | api_or_undeclared, test_failure | ✗✓✓ | 1 of 3 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_replace_6() at default.main() | 规格歧义：边界或非法输入约定 |
| 67 | Dish | test_failure | ✗✓✓✓ | 1 of 4 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_add_dish_1() at default.main() | 题意理解：跨方法状态依赖 |
| 74 | Server | api_or_undeclared, test_failure, type_or_mutability | ✓✓✗✓✓✓ | 1 of 6 tests failed. [test #2 test_failure] An exception has occurred: Exception: Test failed! at default.test_recv_3() at default.main() | 规格歧义：边界或非法输入约定 |

### kimik31p（15 题）

归类计数：API 超时（无代码） 6；规格歧义：边界或非法输入约定 3；规格歧义：功能行为未说明 2；仓颉语义：整数溢出 1；基准缺陷：测试不可执行 1；基准缺陷：题面与参考实现矛盾 1；题意理解：跨方法状态依赖 1

| 题号 | 类名 | 最终失败类别 | 测试通过情况（第一条非超时记录） | 反馈开头 | 人工归类 |
|---|---|---|---|---|---|
| 0 | AccessGatewayFilter | api_timeout, test_failure | ✗✓✓✓ | 1 of 4 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_filter_7() at default.main() Current user: user1, | 规格歧义：功能行为未说明 |
| 1 |  | api_timeout |  |  | API 超时（无代码） |
| 23 | CombinationCalculator | api_timeout, test_failure | ✓✗✓✓✓✓ | 1 of 6 tests failed. [test #1 test_failure] An exception has occurred: Exception: Test failed! at default.test_count_all_2() at default.main() | 仓颉语义：整数溢出 |
| 36 |  | api_timeout |  |  | API 超时（无代码） |
| 39 |  | api_timeout |  |  | API 超时（无代码） |
| 48 | IpUtil | api_or_undeclared | ✓✓✗✓ | error: undeclared identifier 'gethostname' ==> main.cj:48:20: \| 48 \| let hostname = gethostname() \| ^ \| 1 error generated, 1 error printed. | 基准缺陷：测试不可执行 |
| 49 |  | api_timeout |  |  | API 超时（无代码） |
| 53 | LongestWord | api_timeout, test_failure | ✓✗ | 1 of 2 tests failed. [test #1 test_failure] An exception has occurred: Exception: Test failed! at default.test_find_longest_word_4() at default.main() | 基准缺陷：题面与参考实现矛盾 |
| 54 |  | api_timeout |  |  | API 超时（无代码） |
| 57 | MetricsCalculator2 | runtime_exception, test_failure | ✗✓✓ | 1 of 3 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_mrr_8() at default.main() | 规格歧义：边界或非法输入约定 |
| 61 | MusicPlayer | api_timeout, test_failure | ✓✓✗✓✓✓✓✓✓ | 1 of 9 tests failed. [test #2 test_failure] An exception has occurred: Exception: Test failed! at default.test_play_4() at default.main() | 规格歧义：功能行为未说明 |
| 66 |  | api_timeout |  |  | API 超时（无代码） |
| 67 |  | api_or_undeclared, api_timeout | ✗✗✗✗ | [with test #0] error: undeclared type name 'Dish' ==> main.cj:34:44: \| 34 \| if (order.selected_dishes != ArrayList<Dish>([Dish("dish3", 15, 4)])) { \| ^ \| error: | 题意理解：跨方法状态依赖 |
| 74 | Server | test_failure | ✓✓✗✓✓✓ | 1 of 6 tests failed. [test #2 test_failure] An exception has occurred: Exception: Test failed! at default.test_recv_3() at default.main() | 规格歧义：边界或非法输入约定 |
| 81 | Statistics3 | test_failure | ✓✓✓✓✗✓✓✗ | 2 of 8 tests failed. [test #4 test_failure] An exception has occurred: Exception: Test failed! at default.test_correlation_matrix() at default.main() [test #7 t | 规格歧义：边界或非法输入约定 |

## 反馈截断检查

给模型看过的反馈（每题最后一轮之前）按日志中是否存满 1500 字符计数。未存满的，原文也不足 1500 字符，肯定没有被 3000 字符截断；存满的需要重新运行才能确定。

| 模型 | 失败类别 | 未存满（未截断） | 存满（待确定） |
|---|---|---|---|
| doubao_mini | compile_error | 4340 | 1496 |
| doubao_mini | runtime_exception | 44 | 1 |
| doubao_mini | test_failure | 757 | 3 |
| doubao_mini | timeout | 2 | 0 |
| ds_v41f | compile_error | 531 | 150 |
| ds_v41f | runtime_exception | 19 | 1 |
| ds_v41f | test_failure | 1020 | 1 |
| kimik31p | compile_error | 65 | 13 |
| kimik31p | runtime_exception | 5 | 1 |
| kimik31p | test_failure | 105 | 0 |
| kimik31p | timeout | 2 | 0 |

### 重新运行存满的反馈（未截断长度是否超过 3000 字符）

同一题同一份代码只重新运行一次，再按出现次数加权。报错行 = 以 `error:` 开头的行；“保留”指截到前 3000 个字符后该行开头仍在。长度为存满的那些反馈的未截断全文长度（字符）。

| 模型 与 失败类别 | 复查条数（去重后代码） | 超过上限（被截断） | 被截断者的报错行保留 | 报错行全部丢失 | 长度中位数 / 90 分位 / 最大 |
|---|---|---|---|---|---|
| doubao_mini compile_error | 1496（964） | 330 | 4232 / 7311（57.9%） | 0 | 1983 / 5016 / 13882 |
| doubao_mini runtime_exception | 1（1） | 0 | — | 0 | 1019 / 1019 / 1019 |
| doubao_mini test_failure | 3（3） | 0 | — | 0 | 1780 / 1780 / 2442 |
| ds_v41f compile_error | 150（64） | 48 | 625 / 988（63.3%） | 0 | 2109 / 6698 / 16973 |
| ds_v41f runtime_exception | 1（1） | 0 | — | 0 | 2595 / 2595 / 2595 |
| ds_v41f test_failure | 1（1） | 0 | — | 0 | 1728 / 1728 / 1728 |
| kimik31p compile_error | 13（8） | 3 | 46 / 60（76.7%） | 0 | 2026 / 3412 / 4386 |
| kimik31p runtime_exception | 1（1） | 0 | — | 0 | 1949 / 1949 / 1949 |
