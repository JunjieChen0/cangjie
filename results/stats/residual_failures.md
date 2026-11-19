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

## 固定难题：raw / hint / rag 每次重复都失败的题（`direct` 起点，供人工归类）

### ds_v41f（16 题）

| 题号 | 类名 | 最终失败类别 | 测试通过情况（第一条非超时记录） | 反馈开头 | 人工归类 |
|---|---|---|---|---|---|
| 0 | AccessGatewayFilter | foreign_syntax, test_failure | ✗✗✗✗ | error: expected '=>' in lambda expression, found 'set_current_user_info_and_log' ==> main.cj:31:17: \| 31 \| set_current_user_info_and_log(user) \| ^^^^^^^^^^^^^^^ | |
| 4 | Student | test_failure | ✓✓✓✓✗✓✓ | 1 of 7 tests failed. [test #4 test_failure] An exception has occurred: Exception: Test failed! at default.test_get_course_average_1() at default.main() | |
| 16 | Calculator | api_or_undeclared, test_failure | ✗✓✓✓ | 1 of 4 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_calculate_8() at default.main() | |
| 17 | Event | test_failure | ✓✓✓✓✗✓✓ | 1 of 7 tests failed. [test #4 test_failure] An exception has occurred: Exception: Test failed! at default.test_get_available_slots_2() at default.main() | |
| 23 | CombinationCalculator | api_or_undeclared, runtime_exception, test_failure | ✗✗✗✗✗✗ | error: undeclared identifier 'toInt64' ==> main.cj:84:18: \| 84 \| return v.toInt64() \| ^^^^^^^ \| 1 error generated, 1 error printed. | |
| 36 | EmailClient | api_or_undeclared, other_compile, test_failure | ✗✗✗✗✗✗ | error: 'isNone' is not a member of interface 'Any' ==> main.cj:59:35: \| 59 \| if (email["time"].isNone()) { \| ^^^^^^ \| error: invalid binary operator '<' on type | |
| 39 | ExpressionCalculator | api_or_undeclared, test_failure | ✗✗✓✗✓✗✗ | 5 of 7 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_calculate_1() at default.main() 53485150525151504 | |
| 43 | Employee | foreign_syntax, test_failure, type_or_mutability | ✓✓✗✓✓✓ | 1 of 6 tests failed. [test #2 test_failure] An exception has occurred: Exception: Test failed! at default.test_update_employee_6() at default.main() | |
| 48 | IpUtil | api_or_undeclared, foreign_syntax, test_failure | ✓✓✗✗ | 2 of 4 tests failed. [test #2 test_failure] An exception has occurred: Exception: Test failed! at default.test_get_hostname_1() at default.main() [test #3 test_ | |
| 53 | LongestWord | api_or_undeclared, test_failure | ✓✗ | 1 of 2 tests failed. [test #1 test_failure] An exception has occurred: Exception: Test failed! at default.test_find_longest_word_4() at default.main() | |
| 57 | MetricsCalculator2 | api_or_undeclared, foreign_syntax, test_failure | ✗✗✓ | 2 of 3 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_mrr_7() at default.main() [test #1 test_failure]  | |
| 61 | MusicPlayer | test_failure | ✓✓✗✓✓✓✓✓✓ | 1 of 9 tests failed. [test #2 test_failure] An exception has occurred: Exception: Test failed! at default.test_play_4() at default.main() | |
| 65 | NumberWordFormatter | test_failure | ✗✗✓✓✓✓ | 2 of 6 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_format_4() at default.main() [test #1 test_failur | |
| 66 | NumericEntityUnescaper | api_or_undeclared, test_failure | ✗✓✓ | 1 of 3 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_replace_6() at default.main() | |
| 67 | Dish | test_failure | ✗✓✓✓ | 1 of 4 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_add_dish_1() at default.main() | |
| 74 | Server | api_or_undeclared, test_failure, type_or_mutability | ✓✓✗✓✓✓ | 1 of 6 tests failed. [test #2 test_failure] An exception has occurred: Exception: Test failed! at default.test_recv_3() at default.main() | |

### kimik31p（15 题）

| 题号 | 类名 | 最终失败类别 | 测试通过情况（第一条非超时记录） | 反馈开头 | 人工归类 |
|---|---|---|---|---|---|
| 0 | AccessGatewayFilter | api_timeout, test_failure | ✗✓✓✓ | 1 of 4 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_filter_7() at default.main() Current user: user1, | |
| 1 |  | api_timeout |  |  | |
| 23 | CombinationCalculator | api_timeout, test_failure | ✓✗✓✓✓✓ | 1 of 6 tests failed. [test #1 test_failure] An exception has occurred: Exception: Test failed! at default.test_count_all_2() at default.main() | |
| 36 |  | api_timeout |  |  | |
| 39 |  | api_timeout |  |  | |
| 48 | IpUtil | api_or_undeclared | ✓✓✗✓ | error: undeclared identifier 'gethostname' ==> main.cj:48:20: \| 48 \| let hostname = gethostname() \| ^ \| 1 error generated, 1 error printed. | |
| 49 |  | api_timeout |  |  | |
| 53 | LongestWord | api_timeout, test_failure | ✓✗ | 1 of 2 tests failed. [test #1 test_failure] An exception has occurred: Exception: Test failed! at default.test_find_longest_word_4() at default.main() | |
| 54 |  | api_timeout |  |  | |
| 57 | MetricsCalculator2 | runtime_exception, test_failure | ✗✓✓ | 1 of 3 tests failed. [test #0 test_failure] An exception has occurred: Exception: Test failed! at default.test_mrr_8() at default.main() | |
| 61 | MusicPlayer | api_timeout, test_failure | ✓✓✗✓✓✓✓✓✓ | 1 of 9 tests failed. [test #2 test_failure] An exception has occurred: Exception: Test failed! at default.test_play_4() at default.main() | |
| 66 |  | api_timeout |  |  | |
| 67 |  | api_or_undeclared, api_timeout | ✗✗✗✗ | [with test #0] error: undeclared type name 'Dish' ==> main.cj:34:44: \| 34 \| if (order.selected_dishes != ArrayList<Dish>([Dish("dish3", 15, 4)])) { \| ^ \| error: | |
| 74 | Server | test_failure | ✓✓✗✓✓✓ | 1 of 6 tests failed. [test #2 test_failure] An exception has occurred: Exception: Test failed! at default.test_recv_3() at default.main() | |
| 81 | Statistics3 | test_failure | ✓✓✓✓✗✓✓✗ | 2 of 8 tests failed. [test #4 test_failure] An exception has occurred: Exception: Test failed! at default.test_correlation_matrix() at default.main() [test #7 t | |

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

| 模型 与 失败类别 | 复查条数 | 超过上限（被截断） |
|---|---|---|
| ds_v41f compile_error | 150 | 48 |
| ds_v41f runtime_exception | 1 | 0 |
| ds_v41f test_failure | 1 | 0 |
| kimik31p compile_error | 13 | 3 |
| kimik31p runtime_exception | 1 | 0 |
