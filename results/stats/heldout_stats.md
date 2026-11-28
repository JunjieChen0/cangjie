# Original-30 留出测试评测（方案见 docs/留出测试评测方案.md）

题次 12090（无代码 18，出现超时 35）；本机原测试与记录中 `passed` 一致 12090/12090。

## 主要分析

| 范围 | 修复通过的留出失败率 | 第 0 轮通过的留出失败率 | 差（百分点） | 95% CI |
|---|---|---|---|---|
| 全部 30 题 | 6.77%（223/3296） | 2.36%（183/7759） | +4.41 | [-1.37, +11.61] |
| 去掉 1014、1022、1027 | 4.01%（110/2741） | 2.46%（183/7429） | +1.55 | [-2.36, +5.73] |

结论（按预先约定的写法）：未检出修复拟合反馈测试的证据。

## 按反馈方式（修复通过的留出失败率，只做描述）

| 反馈 | 修复通过题次 | 留出失败 | 失败率 |
|---|---|---|---|
| agent | 455 | 39 | 8.57% |
| agent15 | 522 | 39 | 7.47% |
| blind | 311 | 6 | 1.93% |
| hint | 530 | 36 | 6.79% |
| rag | 491 | 28 | 5.7% |
| rag2 | 497 | 42 | 8.45% |
| raw | 490 | 33 | 6.73% |

## 以「原测试与留出测试都通过」重算已有比较（敏感性分析）

| 来源 | 族 | 模型 | 起点 | A vs B | 差 | 95% CI | p(Holm) |
|---|---|---|---|---|---|---|---|
| original30 | - | doubao_mini | direct | hint vs raw | +15.56 | [+6.67, +25.56] | 0.0992 |
| original30 | - | doubao_mini | direct | rag vs raw | +13.33 | [+3.33, +25.56] | 0.6775 |
| original30 | - | doubao_mini | direct | rag vs hint | -2.22 | [-13.33, +8.89] | 1.0000 |
| original30 | - | doubao_mini | direct | raw vs blind | +16.67 | [+5.56, +30.00] | 0.3090 |
| original30 | - | doubao_mini | syntax | hint vs raw | +7.78 | [+1.11, +15.56] | 1.0000 |
| original30 | - | doubao_mini | syntax | rag vs raw | +6.67 | [+0.00, +15.56] | 1.0000 |
| original30 | - | doubao_mini | syntax | rag vs hint | -1.11 | [-11.11, +8.89] | 1.0000 |
| original30 | - | doubao_mini | syntax | raw vs blind | +27.78 | [+14.44, +41.11] | 0.0136 |
| original30 | - | ds_v41f | direct | hint vs raw | -1.11 | [-3.33, +0.00] | 1.0000 |
| original30 | - | ds_v41f | direct | rag vs raw | +2.22 | [+0.00, +6.67] | 1.0000 |
| original30 | - | ds_v41f | direct | rag vs hint | +3.33 | [+0.00, +10.00] | 1.0000 |
| original30 | - | ds_v41f | direct | raw vs blind | +4.44 | [+0.00, +12.22] | 1.0000 |
| original30 | - | ds_v41f | syntax | hint vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| original30 | - | ds_v41f | syntax | rag vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| original30 | - | ds_v41f | syntax | rag vs hint | +0.00 | [+0.00, +0.00] | 1.0000 |
| original30 | - | ds_v41f | syntax | raw vs blind | +0.00 | [+0.00, +0.00] | 1.0000 |
| original30 | - | kimik31p | direct | hint vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | doubao21l | direct | hint vs raw | +15.56 | [+4.44, +28.89] | 1.0000 |
| review_or | G | doubao21l | direct | rag vs raw | +6.67 | [+1.11, +13.33] | 1.0000 |
| review_or | G | doubao21l | direct | rag vs hint | -8.89 | [-23.33, +4.44] | 1.0000 |
| review_or | G | doubao21l | direct | raw vs blind | +17.78 | [+7.78, +30.00] | 0.6003 |
| review_or | G | doubao21l | syntax | hint vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | doubao21l | syntax | rag vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | doubao21l | syntax | rag vs hint | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | doubao21l | syntax | raw vs blind | +2.22 | [+0.00, +5.56] | 1.0000 |
| review_or | G | glm53f | direct | hint vs raw | +0.00 | [-3.33, +3.33] | 1.0000 |
| review_or | G | glm53f | direct | rag vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | glm53f | direct | rag vs hint | +0.00 | [-3.33, +3.33] | 1.0000 |
| review_or | G | glm53f | direct | raw vs blind | +15.56 | [+5.56, +26.67] | 1.0000 |
| review_or | G | glm53f | syntax | hint vs raw | -1.11 | [-3.33, +0.00] | 1.0000 |
| review_or | G | glm53f | syntax | rag vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | glm53f | syntax | rag vs hint | +1.11 | [+0.00, +3.33] | 1.0000 |
| review_or | G | glm53f | syntax | raw vs blind | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | gpt6l | direct | hint vs raw | +2.22 | [+0.00, +6.67] | 1.0000 |
| review_or | G | gpt6l | direct | rag vs raw | +2.22 | [+0.00, +6.67] | 1.0000 |
| review_or | G | gpt6l | direct | rag vs hint | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | gpt6l | direct | raw vs blind | +23.33 | [+10.00, +38.89] | 1.0000 |
| review_or | G | gpt6l | syntax | hint vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | gpt6l | syntax | rag vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | gpt6l | syntax | rag vs hint | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | gpt6l | syntax | raw vs blind | +3.33 | [+0.00, +10.00] | 1.0000 |
| review_or | G | haiku55 | direct | hint vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | haiku55 | direct | rag vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | haiku55 | direct | rag vs hint | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | haiku55 | direct | raw vs blind | +6.67 | [+1.11, +13.33] | 1.0000 |
| review_or | G | haiku55 | syntax | hint vs raw | -1.11 | [-3.33, +0.00] | 1.0000 |
| review_or | G | haiku55 | syntax | rag vs raw | -2.22 | [-6.67, +0.00] | 1.0000 |
| review_or | G | haiku55 | syntax | rag vs hint | -1.11 | [-3.33, +0.00] | 1.0000 |
| review_or | G | haiku55 | syntax | raw vs blind | +2.22 | [+0.00, +5.56] | 1.0000 |
| review_or | G | kimik31p | direct | hint vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | kimik31p | direct | rag vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | kimik31p | direct | rag vs hint | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | kimik31p | direct | raw vs blind | +2.22 | [+0.00, +6.67] | 1.0000 |
| review_or | G | kimik31p | syntax | hint vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | kimik31p | syntax | rag vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | kimik31p | syntax | rag vs hint | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | kimik31p | syntax | raw vs blind | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | mm31f | direct | hint vs raw | +1.11 | [+0.00, +3.33] | 1.0000 |
| review_or | G | mm31f | direct | rag vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | mm31f | direct | rag vs hint | -1.11 | [-3.33, +0.00] | 1.0000 |
| review_or | G | mm31f | direct | raw vs blind | +8.89 | [+1.11, +18.89] | 1.0000 |
| review_or | G | mm31f | syntax | hint vs raw | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | mm31f | syntax | rag vs raw | +1.11 | [+0.00, +3.33] | 1.0000 |
| review_or | G | mm31f | syntax | rag vs hint | +1.11 | [+0.00, +3.33] | 1.0000 |
| review_or | G | mm31f | syntax | raw vs blind | +1.11 | [+0.00, +3.33] | 1.0000 |
| review_or | G | u2f | direct | hint vs raw | +1.11 | [-2.22, +4.44] | 1.0000 |
| review_or | G | u2f | direct | rag vs raw | +2.22 | [+0.00, +5.56] | 1.0000 |
| review_or | G | u2f | direct | rag vs hint | +1.11 | [-2.22, +4.44] | 1.0000 |
| review_or | G | u2f | direct | raw vs blind | +10.00 | [+3.33, +17.78] | 1.0000 |
| review_or | G | u2f | syntax | hint vs raw | +1.11 | [+0.00, +3.33] | 1.0000 |
| review_or | G | u2f | syntax | rag vs raw | +1.11 | [+0.00, +3.33] | 1.0000 |
| review_or | G | u2f | syntax | rag vs hint | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | G | u2f | syntax | raw vs blind | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | A | doubao21l | direct | agent vs rag | -7.78 | [-16.67, -1.11] | 1.0000 |
| review_or | A | doubao21l | direct | agent15 vs agent | +14.44 | [+4.44, +26.67] | 1.0000 |
| review_or | A | doubao21l | syntax | agent vs rag | -1.11 | [-3.33, +0.00] | 1.0000 |
| review_or | A | doubao21l | syntax | agent15 vs agent | +1.11 | [+0.00, +3.33] | 1.0000 |
| review_or | A | doubao_mini | direct | agent vs rag | -7.78 | [-15.56, -0.00] | 1.0000 |
| review_or | A | doubao_mini | direct | agent15 vs agent | +30.00 | [+16.67, +43.33] | 0.0107 |
| review_or | A | doubao_mini | syntax | agent vs rag | -7.78 | [-16.67, -1.11] | 1.0000 |
| review_or | A | doubao_mini | syntax | agent15 vs agent | +8.89 | [+0.00, +18.89] | 1.0000 |
| review_or | A | ds_v41f | direct | agent vs rag | -4.44 | [-12.22, +0.00] | 1.0000 |
| review_or | A | ds_v41f | direct | agent15 vs agent | +1.11 | [+0.00, +3.33] | 1.0000 |
| review_or | A | ds_v41f | syntax | agent vs rag | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | A | ds_v41f | syntax | agent15 vs agent | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | A | glm53f | direct | agent vs rag | -4.44 | [-10.00, +0.00] | 1.0000 |
| review_or | A | glm53f | direct | agent15 vs agent | +5.56 | [+0.00, +12.22] | 1.0000 |
| review_or | A | glm53f | syntax | agent vs rag | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | A | glm53f | syntax | agent15 vs agent | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | A | gpt6l | direct | agent vs rag | -3.33 | [-10.00, +0.00] | 1.0000 |
| review_or | A | gpt6l | direct | agent15 vs agent | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | A | gpt6l | syntax | agent vs rag | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | A | gpt6l | syntax | agent15 vs agent | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | A | haiku55 | direct | agent vs rag | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | A | haiku55 | direct | agent15 vs agent | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | A | haiku55 | syntax | agent vs rag | +2.22 | [+0.00, +6.67] | 1.0000 |
| review_or | A | haiku55 | syntax | agent15 vs agent | -1.11 | [-3.33, +0.00] | 1.0000 |
| review_or | A | kimik31p | direct | agent vs rag | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | A | kimik31p | direct | agent15 vs agent | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | A | kimik31p | syntax | agent vs rag | -1.11 | [-3.33, +0.00] | 1.0000 |
| review_or | A | kimik31p | syntax | agent15 vs agent | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | A | mm31f | direct | agent vs rag | -8.89 | [-18.89, -1.11] | 1.0000 |
| review_or | A | mm31f | direct | agent15 vs agent | +7.78 | [+1.11, +16.67] | 1.0000 |
| review_or | A | mm31f | syntax | agent vs rag | -1.11 | [-3.33, +0.00] | 1.0000 |
| review_or | A | mm31f | syntax | agent15 vs agent | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | A | u2f | direct | agent vs rag | -4.44 | [-12.22, +0.00] | 1.0000 |
| review_or | A | u2f | direct | agent15 vs agent | +3.33 | [+0.00, +10.00] | 1.0000 |
| review_or | A | u2f | syntax | agent vs rag | -2.22 | [-6.67, +0.00] | 1.0000 |
| review_or | A | u2f | syntax | agent15 vs agent | +3.33 | [+0.00, +10.00] | 1.0000 |
| review_or | R | doubao21l | direct | rag2 vs rag | +2.22 | [-5.56, +8.89] | 1.0000 |
| review_or | R | doubao21l | syntax | rag2 vs rag | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | R | doubao_mini | direct | rag2 vs rag | +10.00 | [+0.00, +21.11] | 1.0000 |
| review_or | R | doubao_mini | syntax | rag2 vs rag | -5.56 | [-15.56, +3.33] | 1.0000 |
| review_or | R | ds_v41f | direct | rag2 vs rag | -3.33 | [-10.00, +0.00] | 1.0000 |
| review_or | R | ds_v41f | syntax | rag2 vs rag | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | R | glm53f | direct | rag2 vs rag | -2.22 | [-6.67, +0.00] | 1.0000 |
| review_or | R | glm53f | syntax | rag2 vs rag | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | R | gpt6l | direct | rag2 vs rag | -3.33 | [-10.00, +0.00] | 1.0000 |
| review_or | R | gpt6l | syntax | rag2 vs rag | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | R | haiku55 | direct | rag2 vs rag | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | R | haiku55 | syntax | rag2 vs rag | -1.11 | [-3.33, +0.00] | 1.0000 |
| review_or | R | kimik31p | direct | rag2 vs rag | +0.00 | [+0.00, +0.00] | 1.0000 |
| review_or | R | kimik31p | syntax | rag2 vs rag | -1.11 | [-3.33, +0.00] | 1.0000 |
| review_or | R | mm31f | direct | rag2 vs rag | -2.22 | [-5.56, +0.00] | 1.0000 |
| review_or | R | mm31f | syntax | rag2 vs rag | -1.11 | [-3.33, +0.00] | 1.0000 |
| review_or | R | u2f | direct | rag2 vs rag | -1.11 | [-3.33, +0.00] | 1.0000 |
| review_or | R | u2f | syntax | rag2 vs rag | +0.00 | [+0.00, +0.00] | 1.0000 |

## 每组通过率（本机原测试 O；原测试与留出测试都通过 O&H；均值 ± 标准差）

| 组 | 次数 | O | O&H |
|---|---|---|---|
| doubao21l_or_direct_agent | 3 | 74.44 ± 5.09 | 67.78 ± 5.09 |
| doubao21l_or_direct_agent15 | 3 | 88.89 ± 1.92 | 82.22 ± 1.92 |
| doubao21l_or_direct_blind | 3 | 51.11 ± 8.39 | 51.11 ± 8.39 |
| doubao21l_or_direct_hint | 3 | 91.11 ± 1.92 | 84.44 ± 1.92 |
| doubao21l_or_direct_r0 | 1 | 16.67 ± 0.0 | 16.67 ± 0.0 |
| doubao21l_or_direct_rag | 3 | 80.0 ± 0.0 | 75.56 ± 1.92 |
| doubao21l_or_direct_rag2 | 3 | 83.33 ± 5.77 | 77.78 ± 7.7 |
| doubao21l_or_direct_raw | 3 | 74.44 ± 3.85 | 68.89 ± 5.09 |
| doubao21l_or_syntax_agent | 3 | 95.56 ± 1.92 | 92.22 ± 1.92 |
| doubao21l_or_syntax_agent15 | 3 | 97.78 ± 1.92 | 93.33 ± 0.0 |
| doubao21l_or_syntax_blind | 3 | 94.44 ± 3.85 | 91.11 ± 3.85 |
| doubao21l_or_syntax_hint | 3 | 96.67 ± 0.0 | 93.33 ± 0.0 |
| doubao21l_or_syntax_r0 | 1 | 86.67 ± 0.0 | 83.33 ± 0.0 |
| doubao21l_or_syntax_rag | 3 | 96.67 ± 0.0 | 93.33 ± 0.0 |
| doubao21l_or_syntax_rag2 | 3 | 97.78 ± 1.92 | 93.33 ± 0.0 |
| doubao21l_or_syntax_raw | 3 | 96.67 ± 0.0 | 93.33 ± 0.0 |
| doubao_mini_or_direct_agent | 3 | 33.33 ± 0.0 | 26.67 ± 0.0 |
| doubao_mini_or_direct_agent15 | 3 | 64.44 ± 1.92 | 56.67 ± 3.33 |
| doubao_mini_or_direct_blind | 3 | 4.44 ± 1.92 | 4.44 ± 1.92 |
| doubao_mini_or_direct_hint | 3 | 44.44 ± 7.7 | 36.67 ± 5.77 |
| doubao_mini_or_direct_r0 | 1 | 0.0 ± 0.0 | 0.0 ± 0.0 |
| doubao_mini_or_direct_rag | 3 | 41.11 ± 7.7 | 34.44 ± 5.09 |
| doubao_mini_or_direct_rag2 | 3 | 52.22 ± 1.92 | 44.44 ± 1.92 |
| doubao_mini_or_direct_raw | 3 | 27.78 ± 5.09 | 21.11 ± 3.85 |
| doubao_mini_or_syntax_agent | 3 | 81.11 ± 5.09 | 74.44 ± 5.09 |
| doubao_mini_or_syntax_agent15 | 3 | 90.0 ± 0.0 | 83.33 ± 0.0 |
| doubao_mini_or_syntax_blind | 3 | 51.11 ± 5.09 | 47.78 ± 5.09 |
| doubao_mini_or_syntax_hint | 3 | 90.0 ± 3.33 | 83.33 ± 3.33 |
| doubao_mini_or_syntax_r0 | 1 | 46.67 ± 0.0 | 43.33 ± 0.0 |
| doubao_mini_or_syntax_rag | 3 | 87.78 ± 1.92 | 82.22 ± 1.92 |
| doubao_mini_or_syntax_rag2 | 3 | 83.33 ± 6.67 | 76.67 ± 8.82 |
| doubao_mini_or_syntax_raw | 3 | 82.22 ± 6.94 | 75.56 ± 6.94 |
| ds_v41f_or_direct_agent | 3 | 98.89 ± 1.92 | 95.56 ± 1.92 |
| ds_v41f_or_direct_agent15 | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| ds_v41f_or_direct_blind | 3 | 93.33 ± 0.0 | 93.33 ± 0.0 |
| ds_v41f_or_direct_hint | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| ds_v41f_or_direct_r0 | 1 | 53.33 ± 0.0 | 53.33 ± 0.0 |
| ds_v41f_or_direct_rag | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| ds_v41f_or_direct_rag2 | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| ds_v41f_or_direct_raw | 3 | 98.89 ± 1.92 | 97.78 ± 1.92 |
| ds_v41f_or_syntax_agent | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| ds_v41f_or_syntax_agent15 | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| ds_v41f_or_syntax_blind | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| ds_v41f_or_syntax_hint | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| ds_v41f_or_syntax_r0 | 1 | 90.0 ± 0.0 | 90.0 ± 0.0 |
| ds_v41f_or_syntax_rag | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| ds_v41f_or_syntax_rag2 | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| ds_v41f_or_syntax_raw | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| glm53f_or_direct_agent | 3 | 95.56 ± 1.92 | 92.22 ± 1.92 |
| glm53f_or_direct_agent15 | 3 | 100.0 ± 0.0 | 97.78 ± 1.92 |
| glm53f_or_direct_blind | 3 | 82.22 ± 5.09 | 81.11 ± 6.94 |
| glm53f_or_direct_hint | 3 | 98.89 ± 1.92 | 96.67 ± 3.33 |
| glm53f_or_direct_r0 | 1 | 23.33 ± 0.0 | 23.33 ± 0.0 |
| glm53f_or_direct_rag | 3 | 100.0 ± 0.0 | 96.67 ± 3.33 |
| glm53f_or_direct_rag2 | 3 | 96.67 ± 3.33 | 94.44 ± 3.85 |
| glm53f_or_direct_raw | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| glm53f_or_syntax_agent | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| glm53f_or_syntax_agent15 | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| glm53f_or_syntax_blind | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| glm53f_or_syntax_hint | 3 | 100.0 ± 0.0 | 95.56 ± 1.92 |
| glm53f_or_syntax_r0 | 1 | 90.0 ± 0.0 | 86.67 ± 0.0 |
| glm53f_or_syntax_rag | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| glm53f_or_syntax_rag2 | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| glm53f_or_syntax_raw | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| gpt6l_or_direct_agent | 3 | 98.89 ± 1.92 | 96.67 ± 0.0 |
| gpt6l_or_direct_agent15 | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| gpt6l_or_direct_blind | 3 | 74.44 ± 1.92 | 74.44 ± 1.92 |
| gpt6l_or_direct_hint | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| gpt6l_or_direct_r0 | 1 | 60.0 ± 0.0 | 60.0 ± 0.0 |
| gpt6l_or_direct_rag | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| gpt6l_or_direct_rag2 | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| gpt6l_or_direct_raw | 3 | 97.78 ± 1.92 | 97.78 ± 1.92 |
| gpt6l_or_syntax_agent | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| gpt6l_or_syntax_agent15 | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| gpt6l_or_syntax_blind | 3 | 96.67 ± 0.0 | 96.67 ± 0.0 |
| gpt6l_or_syntax_hint | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| gpt6l_or_syntax_r0 | 1 | 96.67 ± 0.0 | 96.67 ± 0.0 |
| gpt6l_or_syntax_rag | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| gpt6l_or_syntax_rag2 | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| gpt6l_or_syntax_raw | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| haiku55_or_direct_agent | 3 | 100.0 ± 0.0 | 93.33 ± 0.0 |
| haiku55_or_direct_agent15 | 3 | 100.0 ± 0.0 | 93.33 ± 0.0 |
| haiku55_or_direct_blind | 3 | 90.0 ± 3.33 | 86.67 ± 3.33 |
| haiku55_or_direct_hint | 3 | 100.0 ± 0.0 | 93.33 ± 0.0 |
| haiku55_or_direct_r0 | 1 | 73.33 ± 0.0 | 70.0 ± 0.0 |
| haiku55_or_direct_rag | 3 | 100.0 ± 0.0 | 93.33 ± 0.0 |
| haiku55_or_direct_rag2 | 3 | 100.0 ± 0.0 | 93.33 ± 0.0 |
| haiku55_or_direct_raw | 3 | 100.0 ± 0.0 | 93.33 ± 0.0 |
| haiku55_or_syntax_agent | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| haiku55_or_syntax_agent15 | 3 | 100.0 ± 0.0 | 95.56 ± 1.92 |
| haiku55_or_syntax_blind | 3 | 97.78 ± 1.92 | 94.44 ± 1.92 |
| haiku55_or_syntax_hint | 3 | 100.0 ± 0.0 | 95.56 ± 1.92 |
| haiku55_or_syntax_r0 | 1 | 93.33 ± 0.0 | 90.0 ± 0.0 |
| haiku55_or_syntax_rag | 3 | 100.0 ± 0.0 | 94.44 ± 1.92 |
| haiku55_or_syntax_rag2 | 3 | 100.0 ± 0.0 | 93.33 ± 0.0 |
| haiku55_or_syntax_raw | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| kimik31p_or_direct_agent | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| kimik31p_or_direct_agent15 | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| kimik31p_or_direct_blind | 3 | 95.56 ± 3.85 | 94.44 ± 1.92 |
| kimik31p_or_direct_hint | 6 | 99.44 ± 1.36 | 95.0 ± 1.83 |
| kimik31p_or_direct_r0 | 2 | 68.33 ± 2.36 | 66.67 ± 0.0 |
| kimik31p_or_direct_rag | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| kimik31p_or_direct_rag2 | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| kimik31p_or_direct_raw | 6 | 100.0 ± 0.0 | 95.0 ± 1.83 |
| kimik31p_or_syntax_agent | 3 | 98.89 ± 1.92 | 98.89 ± 1.92 |
| kimik31p_or_syntax_agent15 | 3 | 100.0 ± 0.0 | 98.89 ± 1.92 |
| kimik31p_or_syntax_blind | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| kimik31p_or_syntax_hint | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| kimik31p_or_syntax_r0 | 1 | 96.67 ± 0.0 | 96.67 ± 0.0 |
| kimik31p_or_syntax_rag | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| kimik31p_or_syntax_rag2 | 3 | 100.0 ± 0.0 | 98.89 ± 1.92 |
| kimik31p_or_syntax_raw | 3 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| mm31f_or_direct_agent | 3 | 88.89 ± 1.92 | 84.44 ± 1.92 |
| mm31f_or_direct_agent15 | 3 | 95.56 ± 1.92 | 92.22 ± 1.92 |
| mm31f_or_direct_blind | 3 | 87.78 ± 3.85 | 84.44 ± 3.85 |
| mm31f_or_direct_hint | 3 | 97.78 ± 1.92 | 94.44 ± 1.92 |
| mm31f_or_direct_r0 | 1 | 63.33 ± 0.0 | 60.0 ± 0.0 |
| mm31f_or_direct_rag | 3 | 96.67 ± 0.0 | 93.33 ± 0.0 |
| mm31f_or_direct_rag2 | 3 | 96.67 ± 0.0 | 91.11 ± 1.92 |
| mm31f_or_direct_raw | 3 | 96.67 ± 0.0 | 93.33 ± 0.0 |
| mm31f_or_syntax_agent | 3 | 96.67 ± 0.0 | 93.33 ± 0.0 |
| mm31f_or_syntax_agent15 | 3 | 96.67 ± 0.0 | 93.33 ± 0.0 |
| mm31f_or_syntax_blind | 3 | 95.56 ± 1.92 | 92.22 ± 1.92 |
| mm31f_or_syntax_hint | 3 | 96.67 ± 0.0 | 93.33 ± 0.0 |
| mm31f_or_syntax_r0 | 1 | 80.0 ± 0.0 | 76.67 ± 0.0 |
| mm31f_or_syntax_rag | 3 | 97.78 ± 1.92 | 94.44 ± 1.92 |
| mm31f_or_syntax_rag2 | 3 | 96.67 ± 0.0 | 93.33 ± 0.0 |
| mm31f_or_syntax_raw | 3 | 96.67 ± 0.0 | 93.33 ± 0.0 |
| u2f_or_direct_agent | 3 | 96.67 ± 0.0 | 90.0 ± 0.0 |
| u2f_or_direct_agent15 | 3 | 100.0 ± 0.0 | 93.33 ± 0.0 |
| u2f_or_direct_blind | 3 | 86.67 ± 3.33 | 82.22 ± 1.92 |
| u2f_or_direct_hint | 3 | 98.89 ± 1.92 | 93.33 ± 3.33 |
| u2f_or_direct_r0 | 1 | 36.67 ± 0.0 | 36.67 ± 0.0 |
| u2f_or_direct_rag | 3 | 100.0 ± 0.0 | 94.44 ± 1.92 |
| u2f_or_direct_rag2 | 3 | 100.0 ± 0.0 | 93.33 ± 0.0 |
| u2f_or_direct_raw | 3 | 98.89 ± 1.92 | 92.22 ± 1.92 |
| u2f_or_syntax_agent | 3 | 100.0 ± 0.0 | 93.33 ± 0.0 |
| u2f_or_syntax_agent15 | 3 | 100.0 ± 0.0 | 96.67 ± 0.0 |
| u2f_or_syntax_blind | 3 | 97.78 ± 1.92 | 94.44 ± 1.92 |
| u2f_or_syntax_hint | 3 | 98.89 ± 1.92 | 95.56 ± 1.92 |
| u2f_or_syntax_r0 | 1 | 80.0 ± 0.0 | 76.67 ± 0.0 |
| u2f_or_syntax_rag | 3 | 98.89 ± 1.92 | 95.56 ± 1.92 |
| u2f_or_syntax_rag2 | 3 | 98.89 ± 1.92 | 95.56 ± 1.92 |
| u2f_or_syntax_raw | 3 | 97.78 ± 1.92 | 94.44 ± 1.92 |
