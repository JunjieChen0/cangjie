# 补充实验统计（自动生成）

按 docs/补充实验统计方案.md 预先设定的比较族计算；方法同 stage3_stats（按题平均 3 次重复后求差，bootstrap CI，符号翻转置换检验）。成本含共享第 0 轮，rag2 另计查询改写调用。DeepSeek / Doubao-mini 的原有组取自第 3 阶段与 Original-30。

尚未完整的组（1 个，括号内为已完成重复数 / 应有重复数）：glm53f_ce_syntax_rag2（0/3）

第 0 轮与同格其他组不同、不参与配对比较的配置（只列入下表）：glm53f_ce_syntax_agent15（见 docs/补充实验统计方案.md 第九节）。

## 各配置通过率与成本

| 模型 | 数据集 | 起点 | 反馈 | 重复 | 超时题次 | R0 | R5 均值 ± sd | 美元/解（含 R0） |
|---|---|---|---|---|---|---|---|---|
| doubao21l | ce | direct | agent | 3 | 0 | 2.38 | 31.74 ± 1.82 | 0.0418 |
| doubao21l | ce | direct | agent15 | 3 | 0 | 2.38 | 57.54 ± 4.18 | 0.0495 |
| doubao21l | ce | direct | blind | 3 | 0 | 2.38 | 3.57 ± 1.19 | 0.6665 |
| doubao21l | ce | direct | hint | 3 | 0 | 2.38 | 45.24 ± 1.19 | 0.0387 |
| doubao21l | ce | direct | rag | 3 | 0 | 2.38 | 42.07 ± 3.64 | 0.0451 |
| doubao21l | ce | direct | rag2 | 3 | 0 | 2.38 | 42.86 ± 2.38 | 0.0459 |
| doubao21l | ce | direct | raw | 3 | 0 | 2.38 | 31.74 ± 0.69 | 0.0568 |
| doubao21l | ce | syntax | agent | 3 | 0 | 23.81 | 53.57 ± 3.15 | 0.0238 |
| doubao21l | ce | syntax | agent15 | 3 | 0 | 23.81 | 64.68 ± 2.48 | 0.0445 |
| doubao21l | ce | syntax | blind | 3 | 0 | 23.81 | 33.73 ± 1.82 | 0.0580 |
| doubao21l | ce | syntax | hint | 3 | 0 | 23.81 | 53.57 ± 1.19 | 0.0317 |
| doubao21l | ce | syntax | rag | 3 | 0 | 23.81 | 51.19 ± 2.38 | 0.0350 |
| doubao21l | ce | syntax | rag2 | 3 | 0 | 23.81 | 52.78 ± 1.37 | 0.0344 |
| doubao21l | ce | syntax | raw | 3 | 0 | 23.81 | 53.17 ± 1.37 | 0.0312 |
| doubao21l | he | direct | agent | 3 | 0 | 27.44 | 79.27 ± 1.22 | 0.0052 |
| doubao21l | he | direct | agent15 | 3 | 0 | 27.44 | 94.51 ± 1.22 | 0.0056 |
| doubao21l | he | direct | blind | 3 | 0 | 27.44 | 47.56 ± 1.22 | 0.0223 |
| doubao21l | he | direct | hint | 3 | 0 | 27.44 | 90.85 ± 0.61 | 0.0056 |
| doubao21l | he | direct | hint_co | 3 | 0 | 27.44 | 85.98 ± 0.61 | 0.0053 |
| doubao21l | he | direct | rag | 3 | 0 | 27.44 | 88.82 ± 0.35 | 0.0071 |
| doubao21l | he | direct | rag2 | 3 | 0 | 27.44 | 88.41 ± 1.22 | 0.0079 |
| doubao21l | he | direct | rag_co | 3 | 0 | 27.44 | 82.93 ± 1.83 | 0.0063 |
| doubao21l | he | direct | raw | 3 | 0 | 27.44 | 81.10 ± 4.27 | 0.0082 |
| doubao21l | he | direct | raw_co | 3 | 0 | 27.44 | 76.63 ± 1.41 | 0.0077 |
| doubao21l | he | syntax | agent | 3 | 0 | 79.27 | 96.34 ± 0.00 | 0.0033 |
| doubao21l | he | syntax | agent15 | 3 | 0 | 79.27 | 98.78 ± 0.00 | 0.0037 |
| doubao21l | he | syntax | blind | 3 | 0 | 79.27 | 91.87 ± 0.93 | 0.0047 |
| doubao21l | he | syntax | hint | 3 | 0 | 79.27 | 96.75 ± 1.27 | 0.0037 |
| doubao21l | he | syntax | rag | 3 | 0 | 79.27 | 97.76 ± 0.35 | 0.0033 |
| doubao21l | he | syntax | rag2 | 3 | 0 | 79.27 | 97.15 ± 0.35 | 0.0037 |
| doubao21l | he | syntax | raw | 3 | 0 | 79.27 | 95.93 ± 1.41 | 0.0037 |
| doubao21l | or | direct | agent | 3 | 0 | 16.67 | 74.44 ± 5.09 | 0.0060 |
| doubao21l | or | direct | agent15 | 3 | 0 | 16.67 | 88.89 ± 1.92 | 0.0078 |
| doubao21l | or | direct | blind | 3 | 0 | 16.67 | 51.11 ± 8.39 | 0.0233 |
| doubao21l | or | direct | hint | 3 | 0 | 16.67 | 91.11 ± 1.92 | 0.0055 |
| doubao21l | or | direct | rag | 3 | 0 | 16.67 | 80.00 ± 0.00 | 0.0099 |
| doubao21l | or | direct | rag2 | 3 | 0 | 16.67 | 83.33 ± 5.77 | 0.0080 |
| doubao21l | or | direct | raw | 3 | 0 | 16.67 | 74.45 ± 3.85 | 0.0095 |
| doubao21l | or | syntax | agent | 3 | 0 | 86.67 | 95.56 ± 1.93 | 0.0030 |
| doubao21l | or | syntax | agent15 | 3 | 0 | 86.67 | 97.78 ± 1.92 | 0.0036 |
| doubao21l | or | syntax | blind | 3 | 0 | 86.67 | 94.45 ± 3.85 | 0.0042 |
| doubao21l | or | syntax | hint | 3 | 0 | 86.67 | 96.67 ± 0.00 | 0.0029 |
| doubao21l | or | syntax | rag | 3 | 0 | 86.67 | 96.67 ± 0.00 | 0.0031 |
| doubao21l | or | syntax | rag2 | 3 | 0 | 86.67 | 97.78 ± 1.92 | 0.0032 |
| doubao21l | or | syntax | raw | 3 | 0 | 86.67 | 96.67 ± 0.00 | 0.0029 |
| doubao_mini | ce | direct | agent | 3 | 0 | 1.19 | 9.92 ± 1.37 | 0.0416 |
| doubao_mini | ce | direct | agent15 | 3 | 0 | 1.19 | 18.65 ± 4.51 | 0.0637 |
| doubao_mini | ce | direct | blind | 3 | 0 | 1.19 | 1.59 ± 0.69 | 0.3398 |
| doubao_mini | ce | direct | hint | 3 | 0 | 1.19 | 10.31 ± 0.69 | 0.0478 |
| doubao_mini | ce | direct | rag | 3 | 0 | 1.19 | 17.07 ± 0.69 | 0.0291 |
| doubao_mini | ce | direct | rag2 | 3 | 0 | 1.19 | 15.48 ± 2.06 | 0.0404 |
| doubao_mini | ce | direct | raw | 3 | 0 | 1.19 | 8.33 ± 1.19 | 0.0574 |
| doubao_mini | ce | syntax | agent | 3 | 0 | 4.76 | 28.17 ± 0.69 | 0.0170 |
| doubao_mini | ce | syntax | agent15 | 3 | 0 | 4.76 | 36.11 ± 1.37 | 0.0338 |
| doubao_mini | ce | syntax | hint | 3 | 0 | 4.76 | 28.57 ± 2.38 | 0.0201 |
| doubao_mini | ce | syntax | rag | 3 | 0 | 4.76 | 35.31 ± 1.37 | 0.0164 |
| doubao_mini | ce | syntax | rag2 | 3 | 0 | 4.76 | 32.54 ± 1.37 | 0.0210 |
| doubao_mini | ce | syntax | raw | 3 | 0 | 4.76 | 27.38 ± 3.15 | 0.0204 |
| doubao_mini | he | direct | agent | 3 | 0 | 10.98 | 39.23 ± 1.76 | 0.0048 |
| doubao_mini | he | direct | agent15 | 3 | 0 | 10.98 | 62.40 ± 1.26 | 0.0061 |
| doubao_mini | he | direct | blind | 3 | 0 | 10.98 | 14.02 ± 1.61 | 0.0218 |
| doubao_mini | he | direct | hint | 3 | 0 | 10.98 | 51.63 ± 1.86 | 0.0043 |
| doubao_mini | he | direct | hint_co | 3 | 0 | 10.98 | 47.97 ± 2.14 | 0.0040 |
| doubao_mini | he | direct | rag | 3 | 0 | 10.98 | 49.59 ± 1.86 | 0.0051 |
| doubao_mini | he | direct | rag2 | 3 | 0 | 10.98 | 48.58 ± 0.93 | 0.0071 |
| doubao_mini | he | direct | rag_co | 3 | 0 | 10.98 | 45.93 ± 1.27 | 0.0048 |
| doubao_mini | he | direct | raw | 3 | 0 | 10.98 | 35.77 ± 1.76 | 0.0067 |
| doubao_mini | he | direct | raw_co | 3 | 0 | 10.98 | 33.54 ± 1.22 | 0.0065 |
| doubao_mini | he | syntax | agent | 3 | 0 | 48.78 | 82.73 ± 1.54 | 0.0019 |
| doubao_mini | he | syntax | agent15 | 3 | 0 | 48.78 | 89.22 ± 1.27 | 0.0025 |
| doubao_mini | he | syntax | blind | 3 | 0 | 48.78 | 66.66 ± 0.35 | 0.0035 |
| doubao_mini | he | syntax | hint | 3 | 0 | 48.78 | 83.74 ± 1.86 | 0.0021 |
| doubao_mini | he | syntax | rag | 3 | 0 | 48.78 | 88.01 ± 1.26 | 0.0020 |
| doubao_mini | he | syntax | rag2 | 3 | 0 | 48.78 | 88.61 ± 0.93 | 0.0023 |
| doubao_mini | he | syntax | raw | 3 | 0 | 48.78 | 82.52 ± 0.70 | 0.0021 |
| doubao_mini | or | direct | agent | 3 | 0 | 0.00 | 33.33 ± 0.00 | 0.0069 |
| doubao_mini | or | direct | agent15 | 3 | 0 | 0.00 | 64.44 ± 1.93 | 0.0068 |
| doubao_mini | or | direct | blind | 3 | 0 | 0.00 | 4.44 ± 1.93 | 0.0848 |
| doubao_mini | or | direct | hint | 3 | 0 | 0.00 | 44.44 ± 7.70 | 0.0064 |
| doubao_mini | or | direct | rag | 3 | 0 | 0.00 | 41.11 ± 7.70 | 0.0074 |
| doubao_mini | or | direct | rag2 | 3 | 0 | 0.00 | 52.22 ± 1.92 | 0.0076 |
| doubao_mini | or | direct | raw | 3 | 0 | 0.00 | 27.78 ± 5.09 | 0.0105 |
| doubao_mini | or | syntax | agent | 3 | 0 | 46.67 | 81.11 ± 5.09 | 0.0023 |
| doubao_mini | or | syntax | agent15 | 3 | 0 | 46.67 | 90.00 ± 0.00 | 0.0028 |
| doubao_mini | or | syntax | blind | 3 | 0 | 46.67 | 51.11 ± 5.09 | 0.0060 |
| doubao_mini | or | syntax | hint | 3 | 0 | 46.67 | 90.00 ± 3.33 | 0.0023 |
| doubao_mini | or | syntax | rag | 3 | 0 | 46.67 | 87.78 ± 1.92 | 0.0024 |
| doubao_mini | or | syntax | rag2 | 3 | 0 | 46.67 | 83.33 ± 6.67 | 0.0031 |
| doubao_mini | or | syntax | raw | 3 | 0 | 46.67 | 82.22 ± 6.94 | 0.0026 |
| ds_v41f | ce | direct | agent | 3 | 0 | 25.00 | 67.46 ± 0.69 | 0.0658 |
| ds_v41f | ce | direct | agent15 | 3 | 0 | 25.00 | 76.19 ± 1.19 | 0.1072 |
| ds_v41f | ce | direct | blind | 3 | 0 | 25.00 | 42.86 ± 2.38 | 0.1863 |
| ds_v41f | ce | direct | hint | 3 | 0 | 25.00 | 69.45 ± 2.99 | 0.1011 |
| ds_v41f | ce | direct | rag | 3 | 0 | 25.00 | 72.22 ± 2.48 | 0.0949 |
| ds_v41f | ce | direct | rag2 | 3 | 0 | 25.00 | 71.03 ± 3.64 | 0.1034 |
| ds_v41f | ce | direct | raw | 3 | 0 | 25.00 | 68.26 ± 1.82 | 0.1074 |
| ds_v41f | ce | syntax | agent | 3 | 0 | 39.29 | 65.08 ± 3.64 | 0.0724 |
| ds_v41f | ce | syntax | agent15 | 3 | 0 | 39.29 | 75.00 ± 1.19 | 0.1263 |
| ds_v41f | ce | syntax | blind | 3 | 0 | 39.29 | 47.62 ± 0.00 | 0.1481 |
| ds_v41f | ce | syntax | hint | 3 | 0 | 39.29 | 69.84 ± 1.82 | 0.0998 |
| ds_v41f | ce | syntax | rag | 3 | 0 | 39.29 | 68.26 ± 2.75 | 0.1035 |
| ds_v41f | ce | syntax | rag2 | 3 | 0 | 39.29 | 68.65 ± 1.82 | 0.1088 |
| ds_v41f | ce | syntax | raw | 3 | 0 | 39.29 | 67.46 ± 1.37 | 0.1076 |
| ds_v41f | he | direct | agent | 3 | 0 | 75.00 | 98.98 ± 0.93 | 0.0065 |
| ds_v41f | he | direct | agent15 | 3 | 0 | 75.00 | 100.00 ± 0.00 | 0.0067 |
| ds_v41f | he | direct | blind | 3 | 0 | 75.00 | 96.75 ± 0.70 | 0.0117 |
| ds_v41f | he | direct | hint | 3 | 0 | 75.00 | 99.80 ± 0.35 | 0.0068 |
| ds_v41f | he | direct | hint_co | 3 | 0 | 75.00 | 94.71 ± 1.27 | 0.0063 |
| ds_v41f | he | direct | rag | 3 | 0 | 75.00 | 99.80 ± 0.35 | 0.0072 |
| ds_v41f | he | direct | rag2 | 3 | 0 | 75.00 | 99.80 ± 0.35 | 0.0078 |
| ds_v41f | he | direct | rag_co | 3 | 0 | 75.00 | 94.51 ± 0.61 | 0.0064 |
| ds_v41f | he | direct | raw | 3 | 0 | 75.00 | 99.80 ± 0.35 | 0.0070 |
| ds_v41f | he | direct | raw_co | 3 | 0 | 75.00 | 94.71 ± 0.35 | 0.0065 |
| ds_v41f | he | syntax | agent | 3 | 0 | 89.63 | 99.39 ± 0.00 | 0.0047 |
| ds_v41f | he | syntax | agent15 | 3 | 0 | 89.02 | 100.00 ± 0.00 | 0.0051 |
| ds_v41f | he | syntax | blind | 3 | 0 | 89.63 | 98.37 ± 0.35 | 0.0062 |
| ds_v41f | he | syntax | hint | 3 | 0 | 89.02 | 100.00 ± 0.00 | 0.0053 |
| ds_v41f | he | syntax | rag | 3 | 0 | 89.02 | 100.00 ± 0.00 | 0.0049 |
| ds_v41f | he | syntax | rag2 | 3 | 0 | 89.02 | 99.59 ± 0.35 | 0.0051 |
| ds_v41f | he | syntax | raw | 3 | 0 | 89.63 | 100.00 ± 0.00 | 0.0052 |
| ds_v41f | or | direct | agent | 3 | 0 | 53.33 | 98.89 ± 1.92 | 0.0074 |
| ds_v41f | or | direct | agent15 | 3 | 0 | 53.33 | 100.00 ± 0.00 | 0.0074 |
| ds_v41f | or | direct | blind | 3 | 0 | 53.33 | 93.33 ± 0.00 | 0.0168 |
| ds_v41f | or | direct | hint | 3 | 0 | 53.33 | 100.00 ± 0.00 | 0.0075 |
| ds_v41f | or | direct | rag | 3 | 0 | 53.33 | 100.00 ± 0.00 | 0.0088 |
| ds_v41f | or | direct | rag2 | 3 | 0 | 53.33 | 100.00 ± 0.00 | 0.0086 |
| ds_v41f | or | direct | raw | 3 | 0 | 53.33 | 98.89 ± 1.92 | 0.0087 |
| ds_v41f | or | syntax | agent | 3 | 0 | 90.00 | 100.00 ± 0.00 | 0.0055 |
| ds_v41f | or | syntax | agent15 | 3 | 0 | 90.00 | 100.00 ± 0.00 | 0.0056 |
| ds_v41f | or | syntax | blind | 3 | 0 | 90.00 | 100.00 ± 0.00 | 0.0074 |
| ds_v41f | or | syntax | hint | 3 | 0 | 90.00 | 100.00 ± 0.00 | 0.0058 |
| ds_v41f | or | syntax | rag | 3 | 0 | 90.00 | 100.00 ± 0.00 | 0.0059 |
| ds_v41f | or | syntax | rag2 | 3 | 0 | 90.00 | 100.00 ± 0.00 | 0.0059 |
| ds_v41f | or | syntax | raw | 3 | 0 | 90.00 | 100.00 ± 0.00 | 0.0057 |
| glm53f | ce | direct | agent | 3 | 2 | 16.67 | 69.45 ± 2.48 | 0.0761 |
| glm53f | ce | direct | agent15 | 3 | 1 | 16.67 | 83.33 ± 0.00 | 0.1451 |
| glm53f | ce | direct | blind | 3 | 0 | 16.67 | 27.78 ± 3.64 | 0.5587 |
| glm53f | ce | direct | hint | 3 | 3 | 16.67 | 73.41 ± 1.82 | 0.0856 |
| glm53f | ce | direct | rag | 3 | 21 | 16.67 | 71.83 ± 1.82 | 0.0870 |
| glm53f | ce | direct | rag2 | 3 | 1 | 16.67 | 72.62 ± 4.29 | 0.1075 |
| glm53f | ce | direct | raw | 3 | 0 | 16.67 | 70.64 ± 3.44 | 0.1142 |
| glm53f | ce | syntax | agent | 3 | 1 | 28.57 | 74.21 ± 4.18 | 0.0874 |
| glm53f | ce | syntax | agent15 | 3 | 13 | 38.10 | 80.55 ± 1.82 | 0.1483 |
| glm53f | ce | syntax | blind | 3 | 1 | 33.33 | 57.54 ± 1.82 | 0.1978 |
| glm53f | ce | syntax | hint | 3 | 1 | 29.76 | 76.59 ± 1.82 | 0.1007 |
| glm53f | ce | syntax | rag | 3 | 4 | 33.33 | 73.41 ± 0.69 | 0.1042 |
| glm53f | ce | syntax | raw | 3 | 3 | 33.33 | 77.38 ± 0.00 | 0.0989 |
| glm53f | he | direct | agent | 3 | 0 | 59.15 | 99.80 ± 0.35 | 0.0041 |
| glm53f | he | direct | agent15 | 3 | 0 | 59.15 | 100.00 ± 0.00 | 0.0042 |
| glm53f | he | direct | blind | 3 | 0 | 59.15 | 90.65 ± 2.47 | 0.0289 |
| glm53f | he | direct | hint | 3 | 1 | 59.15 | 99.80 ± 0.35 | 0.0051 |
| glm53f | he | direct | hint_co | 3 | 0 | 59.15 | 97.15 ± 0.70 | 0.0043 |
| glm53f | he | direct | rag | 3 | 0 | 59.15 | 99.19 ± 0.35 | 0.0072 |
| glm53f | he | direct | rag2 | 3 | 0 | 59.15 | 99.59 ± 0.35 | 0.0052 |
| glm53f | he | direct | rag_co | 3 | 0 | 59.15 | 96.75 ± 1.27 | 0.0045 |
| glm53f | he | direct | raw | 3 | 0 | 59.15 | 99.39 ± 0.00 | 0.0061 |
| glm53f | he | direct | raw_co | 3 | 0 | 59.15 | 97.15 ± 0.35 | 0.0042 |
| glm53f | he | syntax | agent | 3 | 0 | 92.68 | 100.00 ± 0.00 | 0.0029 |
| glm53f | he | syntax | agent15 | 3 | 0 | 92.68 | 100.00 ± 0.00 | 0.0028 |
| glm53f | he | syntax | blind | 3 | 0 | 92.68 | 100.00 ± 0.00 | 0.0033 |
| glm53f | he | syntax | hint | 3 | 0 | 92.68 | 100.00 ± 0.00 | 0.0028 |
| glm53f | he | syntax | rag | 3 | 0 | 92.68 | 100.00 ± 0.00 | 0.0028 |
| glm53f | he | syntax | rag2 | 3 | 0 | 92.68 | 100.00 ± 0.00 | 0.0028 |
| glm53f | he | syntax | raw | 3 | 0 | 92.68 | 100.00 ± 0.00 | 0.0029 |
| glm53f | or | direct | agent | 3 | 0 | 23.33 | 95.56 ± 1.93 | 0.0070 |
| glm53f | or | direct | agent15 | 3 | 0 | 23.33 | 100.00 ± 0.00 | 0.0104 |
| glm53f | or | direct | blind | 3 | 0 | 23.33 | 82.22 ± 5.09 | 0.0395 |
| glm53f | or | direct | hint | 3 | 0 | 23.33 | 98.89 ± 1.92 | 0.0075 |
| glm53f | or | direct | rag | 3 | 0 | 23.33 | 100.00 ± 0.00 | 0.0067 |
| glm53f | or | direct | rag2 | 3 | 0 | 23.33 | 96.67 ± 3.34 | 0.0128 |
| glm53f | or | direct | raw | 3 | 0 | 23.33 | 100.00 ± 0.00 | 0.0088 |
| glm53f | or | syntax | agent | 3 | 0 | 90.00 | 100.00 ± 0.00 | 0.0032 |
| glm53f | or | syntax | agent15 | 3 | 0 | 90.00 | 100.00 ± 0.00 | 0.0031 |
| glm53f | or | syntax | blind | 3 | 0 | 90.00 | 100.00 ± 0.00 | 0.0041 |
| glm53f | or | syntax | hint | 3 | 0 | 90.00 | 100.00 ± 0.00 | 0.0037 |
| glm53f | or | syntax | rag | 3 | 0 | 90.00 | 100.00 ± 0.00 | 0.0032 |
| glm53f | or | syntax | rag2 | 3 | 0 | 90.00 | 100.00 ± 0.00 | 0.0037 |
| glm53f | or | syntax | raw | 3 | 0 | 90.00 | 100.00 ± 0.00 | 0.0034 |
| gpt6l | ce | direct | agent | 3 | 0 | 25.00 | 61.90 ± 2.39 | 0.0068 |
| gpt6l | ce | direct | agent15 | 3 | 0 | 25.00 | 71.43 ± 2.06 | 0.0164 |
| gpt6l | ce | direct | blind | 3 | 0 | 25.00 | 37.30 ± 2.48 | 0.0157 |
| gpt6l | ce | direct | hint | 3 | 0 | 25.00 | 59.52 ± 1.19 | 0.0081 |
| gpt6l | ce | direct | rag | 3 | 0 | 25.00 | 61.90 ± 1.20 | 0.0084 |
| gpt6l | ce | direct | rag2 | 3 | 0 | 25.00 | 59.12 ± 0.69 | 0.0100 |
| gpt6l | ce | direct | raw | 3 | 0 | 23.81 | 59.52 ± 2.06 | 0.0082 |
| gpt6l | ce | syntax | agent | 3 | 0 | 28.57 | 62.70 ± 1.38 | 0.0077 |
| gpt6l | ce | syntax | agent15 | 3 | 0 | 28.57 | 68.26 ± 1.82 | 0.0203 |
| gpt6l | ce | syntax | blind | 3 | 0 | 28.57 | 40.48 ± 1.19 | 0.0152 |
| gpt6l | ce | syntax | hint | 3 | 0 | 28.57 | 61.90 ± 1.20 | 0.0085 |
| gpt6l | ce | syntax | rag | 3 | 0 | 28.57 | 61.90 ± 0.00 | 0.0092 |
| gpt6l | ce | syntax | rag2 | 3 | 0 | 28.57 | 62.30 ± 1.38 | 0.0100 |
| gpt6l | ce | syntax | raw | 3 | 0 | 28.57 | 61.90 ± 1.20 | 0.0083 |
| gpt6l | he | direct | agent | 3 | 0 | 60.37 | 94.51 ± 2.11 | 0.0009 |
| gpt6l | he | direct | agent15 | 3 | 0 | 60.37 | 97.76 ± 1.54 | 0.0013 |
| gpt6l | he | direct | blind | 3 | 0 | 60.37 | 80.08 ± 0.93 | 0.0022 |
| gpt6l | he | direct | hint | 3 | 0 | 60.37 | 97.15 ± 0.35 | 0.0009 |
| gpt6l | he | direct | hint_co | 3 | 0 | 60.37 | 94.10 ± 0.35 | 0.0008 |
| gpt6l | he | direct | rag | 3 | 0 | 60.37 | 96.14 ± 0.70 | 0.0011 |
| gpt6l | he | direct | rag2 | 3 | 0 | 60.37 | 95.93 ± 0.93 | 0.0012 |
| gpt6l | he | direct | rag_co | 3 | 0 | 60.37 | 93.09 ± 0.70 | 0.0009 |
| gpt6l | he | direct | raw | 3 | 0 | 60.37 | 95.73 ± 0.61 | 0.0011 |
| gpt6l | he | direct | raw_co | 3 | 0 | 60.37 | 92.88 ± 1.27 | 0.0009 |
| gpt6l | he | syntax | agent | 3 | 0 | 87.80 | 98.58 ± 0.35 | 0.0008 |
| gpt6l | he | syntax | agent15 | 3 | 0 | 87.80 | 98.78 ± 0.00 | 0.0010 |
| gpt6l | he | syntax | blind | 3 | 0 | 87.80 | 95.32 ± 0.70 | 0.0009 |
| gpt6l | he | syntax | hint | 3 | 0 | 87.80 | 97.76 ± 0.35 | 0.0008 |
| gpt6l | he | syntax | rag | 3 | 0 | 87.80 | 98.98 ± 0.35 | 0.0008 |
| gpt6l | he | syntax | rag2 | 3 | 0 | 87.80 | 98.17 ± 0.61 | 0.0009 |
| gpt6l | he | syntax | raw | 3 | 0 | 87.80 | 98.98 ± 0.70 | 0.0007 |
| gpt6l | or | direct | agent | 3 | 0 | 60.00 | 98.89 ± 1.92 | 0.0010 |
| gpt6l | or | direct | agent15 | 3 | 0 | 60.00 | 100.00 ± 0.00 | 0.0011 |
| gpt6l | or | direct | blind | 3 | 0 | 60.00 | 74.44 ± 1.93 | 0.0024 |
| gpt6l | or | direct | hint | 3 | 0 | 60.00 | 100.00 ± 0.00 | 0.0010 |
| gpt6l | or | direct | rag | 3 | 0 | 60.00 | 100.00 ± 0.00 | 0.0011 |
| gpt6l | or | direct | rag2 | 3 | 0 | 60.00 | 100.00 ± 0.00 | 0.0012 |
| gpt6l | or | direct | raw | 3 | 0 | 60.00 | 97.78 ± 1.92 | 0.0011 |
| gpt6l | or | syntax | agent | 3 | 0 | 96.67 | 100.00 ± 0.00 | 0.0007 |
| gpt6l | or | syntax | agent15 | 3 | 0 | 96.67 | 100.00 ± 0.00 | 0.0007 |
| gpt6l | or | syntax | blind | 3 | 0 | 96.67 | 96.67 ± 0.00 | 0.0010 |
| gpt6l | or | syntax | hint | 3 | 0 | 96.67 | 100.00 ± 0.00 | 0.0007 |
| gpt6l | or | syntax | rag | 3 | 0 | 96.67 | 100.00 ± 0.00 | 0.0007 |
| gpt6l | or | syntax | rag2 | 3 | 0 | 96.67 | 100.00 ± 0.00 | 0.0008 |
| gpt6l | or | syntax | raw | 3 | 0 | 96.67 | 100.00 ± 0.00 | 0.0007 |
| haiku55 | ce | direct | agent | 3 | 0 | 25.00 | 65.48 ± 0.00 | 0.0115 |
| haiku55 | ce | direct | agent15 | 3 | 0 | 25.00 | 67.46 ± 0.69 | 0.0285 |
| haiku55 | ce | direct | blind | 3 | 0 | 25.00 | 34.52 ± 2.38 | 0.0308 |
| haiku55 | ce | direct | hint | 3 | 0 | 25.00 | 65.08 ± 1.82 | 0.0124 |
| haiku55 | ce | direct | rag | 3 | 0 | 25.00 | 64.29 ± 1.19 | 0.0139 |
| haiku55 | ce | direct | rag2 | 3 | 0 | 25.00 | 65.48 ± 1.19 | 0.0144 |
| haiku55 | ce | direct | raw | 3 | 0 | 25.00 | 64.29 ± 3.58 | 0.0129 |
| haiku55 | ce | syntax | agent | 3 | 0 | 39.29 | 63.10 ± 0.00 | 0.0131 |
| haiku55 | ce | syntax | agent15 | 3 | 0 | 39.29 | 66.27 ± 1.82 | 0.0308 |
| haiku55 | ce | syntax | blind | 3 | 0 | 39.29 | 50.00 ± 1.19 | 0.0212 |
| haiku55 | ce | syntax | hint | 3 | 0 | 39.29 | 64.29 ± 1.19 | 0.0142 |
| haiku55 | ce | syntax | rag | 3 | 0 | 39.29 | 63.89 ± 0.69 | 0.0156 |
| haiku55 | ce | syntax | rag2 | 3 | 0 | 39.29 | 63.50 ± 0.69 | 0.0164 |
| haiku55 | ce | syntax | raw | 3 | 0 | 39.29 | 64.69 ± 0.69 | 0.0144 |
| haiku55 | he | direct | agent | 3 | 0 | 77.44 | 100.00 ± 0.00 | 0.0007 |
| haiku55 | he | direct | agent15 | 3 | 0 | 77.44 | 100.00 ± 0.00 | 0.0007 |
| haiku55 | he | direct | blind | 3 | 0 | 77.44 | 92.68 ± 1.22 | 0.0012 |
| haiku55 | he | direct | hint | 3 | 0 | 77.44 | 100.00 ± 0.00 | 0.0007 |
| haiku55 | he | direct | hint_co | 3 | 0 | 77.44 | 99.39 ± 0.00 | 0.0007 |
| haiku55 | he | direct | rag | 3 | 0 | 77.44 | 100.00 ± 0.00 | 0.0007 |
| haiku55 | he | direct | rag2 | 3 | 0 | 77.44 | 100.00 ± 0.00 | 0.0008 |
| haiku55 | he | direct | rag_co | 3 | 0 | 77.44 | 99.19 ± 0.35 | 0.0007 |
| haiku55 | he | direct | raw | 3 | 0 | 77.44 | 100.00 ± 0.00 | 0.0007 |
| haiku55 | he | direct | raw_co | 3 | 0 | 77.44 | 98.98 ± 0.70 | 0.0007 |
| haiku55 | he | syntax | agent | 3 | 0 | 93.29 | 99.80 ± 0.35 | 0.0010 |
| haiku55 | he | syntax | agent15 | 3 | 0 | 93.29 | 100.00 ± 0.00 | 0.0010 |
| haiku55 | he | syntax | blind | 3 | 0 | 93.29 | 99.19 ± 0.35 | 0.0011 |
| haiku55 | he | syntax | hint | 3 | 0 | 93.29 | 100.00 ± 0.00 | 0.0010 |
| haiku55 | he | syntax | rag | 3 | 0 | 93.29 | 99.80 ± 0.35 | 0.0010 |
| haiku55 | he | syntax | rag2 | 3 | 0 | 93.29 | 100.00 ± 0.00 | 0.0010 |
| haiku55 | he | syntax | raw | 3 | 0 | 93.29 | 100.00 ± 0.00 | 0.0010 |
| haiku55 | or | direct | agent | 3 | 0 | 73.33 | 100.00 ± 0.00 | 0.0008 |
| haiku55 | or | direct | agent15 | 3 | 0 | 73.33 | 100.00 ± 0.00 | 0.0008 |
| haiku55 | or | direct | blind | 3 | 0 | 73.33 | 90.00 ± 3.33 | 0.0018 |
| haiku55 | or | direct | hint | 3 | 0 | 73.33 | 100.00 ± 0.00 | 0.0008 |
| haiku55 | or | direct | rag | 3 | 0 | 73.33 | 100.00 ± 0.00 | 0.0009 |
| haiku55 | or | direct | rag2 | 3 | 0 | 73.33 | 100.00 ± 0.00 | 0.0010 |
| haiku55 | or | direct | raw | 3 | 0 | 73.33 | 100.00 ± 0.00 | 0.0009 |
| haiku55 | or | syntax | agent | 3 | 0 | 93.33 | 100.00 ± 0.00 | 0.0011 |
| haiku55 | or | syntax | agent15 | 3 | 0 | 93.33 | 100.00 ± 0.00 | 0.0012 |
| haiku55 | or | syntax | blind | 3 | 0 | 93.33 | 97.78 ± 1.92 | 0.0015 |
| haiku55 | or | syntax | hint | 3 | 0 | 93.33 | 100.00 ± 0.00 | 0.0012 |
| haiku55 | or | syntax | rag | 3 | 0 | 93.33 | 100.00 ± 0.00 | 0.0011 |
| haiku55 | or | syntax | rag2 | 3 | 0 | 93.33 | 100.00 ± 0.00 | 0.0012 |
| haiku55 | or | syntax | raw | 3 | 0 | 93.33 | 100.00 ± 0.00 | 0.0011 |
| kimik31p | ce | direct | agent | 3 | 0 | 35.71 | 75.79 ± 2.99 | 0.2607 |
| kimik31p | ce | direct | agent15 | 3 | 0 | 35.71 | 92.86 ± 3.15 | 0.2894 |
| kimik31p | ce | direct | blind | 3 | 0 | 35.71 | 56.74 ± 2.48 | 0.6226 |
| kimik31p | ce | direct | hint | 3 | 0 | 35.71 | 78.57 ± 2.38 | 0.3739 |
| kimik31p | ce | direct | rag | 3 | 0 | 35.71 | 80.16 ± 0.69 | 0.3383 |
| kimik31p | ce | direct | rag2 | 3 | 0 | 35.71 | 77.78 ± 1.82 | 0.4056 |
| kimik31p | ce | direct | raw | 3 | 0 | 35.71 | 77.38 ± 2.06 | 0.4157 |
| kimik31p | ce | syntax | agent | 3 | 0 | 38.10 | 81.35 ± 0.69 | 0.2617 |
| kimik31p | ce | syntax | agent15 | 3 | 0 | 38.10 | 92.46 ± 1.37 | 0.3144 |
| kimik31p | ce | syntax | blind | 3 | 0 | 38.10 | 59.12 ± 1.37 | 0.5567 |
| kimik31p | ce | syntax | hint | 3 | 0 | 38.10 | 82.14 ± 2.38 | 0.3631 |
| kimik31p | ce | syntax | rag | 3 | 0 | 38.10 | 81.35 ± 1.82 | 0.3827 |
| kimik31p | ce | syntax | rag2 | 3 | 0 | 38.10 | 79.76 ± 3.15 | 0.4006 |
| kimik31p | ce | syntax | raw | 3 | 0 | 38.10 | 80.55 ± 2.99 | 0.4040 |
| kimik31p | he | direct | agent | 3 | 0 | 75.00 | 99.80 ± 0.35 | 0.0274 |
| kimik31p | he | direct | agent15 | 3 | 0 | 75.00 | 100.00 ± 0.00 | 0.0273 |
| kimik31p | he | direct | blind | 3 | 0 | 75.00 | 99.39 ± 0.00 | 0.0451 |
| kimik31p | he | direct | hint | 3 | 0 | 75.00 | 100.00 ± 0.00 | 0.0289 |
| kimik31p | he | direct | hint_co | 3 | 0 | 75.00 | 98.17 ± 0.61 | 0.0272 |
| kimik31p | he | direct | rag | 3 | 0 | 75.00 | 100.00 ± 0.00 | 0.0285 |
| kimik31p | he | direct | rag2 | 3 | 0 | 75.00 | 100.00 ± 0.00 | 0.0288 |
| kimik31p | he | direct | rag_co | 3 | 0 | 75.00 | 98.37 ± 0.35 | 0.0277 |
| kimik31p | he | direct | raw | 3 | 0 | 75.00 | 100.00 ± 0.00 | 0.0294 |
| kimik31p | he | direct | raw_co | 3 | 0 | 75.00 | 97.76 ± 0.35 | 0.0285 |
| kimik31p | he | syntax | agent | 3 | 0 | 92.07 | 99.80 ± 0.35 | 0.0247 |
| kimik31p | he | syntax | agent15 | 3 | 0 | 92.68 | 100.00 ± 0.00 | 0.0240 |
| kimik31p | he | syntax | blind | 3 | 0 | 92.68 | 99.59 ± 0.35 | 0.0283 |
| kimik31p | he | syntax | hint | 3 | 0 | 92.68 | 100.00 ± 0.00 | 0.0240 |
| kimik31p | he | syntax | rag | 3 | 0 | 92.68 | 100.00 ± 0.00 | 0.0249 |
| kimik31p | he | syntax | rag2 | 3 | 0 | 92.07 | 100.00 ± 0.00 | 0.0255 |
| kimik31p | he | syntax | raw | 3 | 0 | 92.68 | 100.00 ± 0.00 | 0.0247 |
| kimik31p | or | direct | agent | 3 | 0 | 66.67 | 100.00 ± 0.00 | 0.0278 |
| kimik31p | or | direct | agent15 | 3 | 0 | 66.67 | 100.00 ± 0.00 | 0.0271 |
| kimik31p | or | direct | blind | 3 | 0 | 66.67 | 95.55 ± 3.85 | 0.0653 |
| kimik31p | or | direct | hint | 3 | 0 | 66.67 | 100.00 ± 0.00 | 0.0273 |
| kimik31p | or | direct | rag | 3 | 0 | 66.67 | 100.00 ± 0.00 | 0.0302 |
| kimik31p | or | direct | rag2 | 3 | 0 | 66.67 | 100.00 ± 0.00 | 0.0280 |
| kimik31p | or | direct | raw | 3 | 0 | 66.67 | 100.00 ± 0.00 | 0.0285 |
| kimik31p | or | syntax | agent | 3 | 0 | 96.67 | 98.89 ± 1.92 | 0.0284 |
| kimik31p | or | syntax | agent15 | 3 | 0 | 96.67 | 100.00 ± 0.00 | 0.0293 |
| kimik31p | or | syntax | blind | 3 | 0 | 96.67 | 100.00 ± 0.00 | 0.0279 |
| kimik31p | or | syntax | hint | 3 | 0 | 96.67 | 100.00 ± 0.00 | 0.0273 |
| kimik31p | or | syntax | rag | 3 | 0 | 96.67 | 100.00 ± 0.00 | 0.0295 |
| kimik31p | or | syntax | rag2 | 3 | 0 | 96.67 | 100.00 ± 0.00 | 0.0346 |
| kimik31p | or | syntax | raw | 3 | 0 | 96.67 | 100.00 ± 0.00 | 0.0298 |
| mm31f | ce | direct | agent | 3 | 0 | 26.19 | 54.76 ± 2.06 | 0.0294 |
| mm31f | ce | direct | agent15 | 3 | 0 | 26.19 | 63.49 ± 1.82 | 0.0441 |
| mm31f | ce | direct | blind | 3 | 0 | 26.19 | 45.64 ± 0.69 | 0.0752 |
| mm31f | ce | direct | hint | 3 | 0 | 26.19 | 65.08 ± 1.82 | 0.0473 |
| mm31f | ce | direct | rag | 3 | 0 | 26.19 | 61.90 ± 2.39 | 0.0531 |
| mm31f | ce | direct | rag2 | 3 | 0 | 26.19 | 65.08 ± 2.48 | 0.0507 |
| mm31f | ce | direct | raw | 3 | 0 | 26.19 | 65.08 ± 1.37 | 0.0471 |
| mm31f | ce | syntax | agent | 3 | 0 | 36.90 | 62.30 ± 1.82 | 0.0250 |
| mm31f | ce | syntax | agent15 | 3 | 0 | 36.90 | 66.67 ± 1.19 | 0.0414 |
| mm31f | ce | syntax | blind | 3 | 0 | 36.90 | 50.79 ± 1.37 | 0.0639 |
| mm31f | ce | syntax | hint | 3 | 0 | 36.90 | 66.27 ± 0.69 | 0.0429 |
| mm31f | ce | syntax | rag | 3 | 0 | 36.90 | 66.67 ± 1.19 | 0.0449 |
| mm31f | ce | syntax | rag2 | 3 | 0 | 36.90 | 67.07 ± 0.69 | 0.0443 |
| mm31f | ce | syntax | raw | 3 | 0 | 36.90 | 66.67 ± 1.19 | 0.0432 |
| mm31f | he | direct | agent | 3 | 0 | 70.12 | 96.34 ± 0.00 | 0.0033 |
| mm31f | he | direct | agent15 | 3 | 0 | 70.12 | 98.58 ± 0.35 | 0.0037 |
| mm31f | he | direct | blind | 3 | 0 | 70.12 | 92.07 ± 1.61 | 0.0072 |
| mm31f | he | direct | hint | 3 | 0 | 70.12 | 98.58 ± 0.35 | 0.0040 |
| mm31f | he | direct | hint_co | 3 | 0 | 70.12 | 91.46 ± 0.61 | 0.0036 |
| mm31f | he | direct | rag | 3 | 0 | 70.12 | 99.39 ± 0.00 | 0.0038 |
| mm31f | he | direct | rag2 | 3 | 0 | 70.12 | 99.39 ± 0.00 | 0.0039 |
| mm31f | he | direct | rag_co | 3 | 0 | 70.12 | 92.48 ± 0.70 | 0.0036 |
| mm31f | he | direct | raw | 3 | 0 | 70.12 | 97.36 ± 0.35 | 0.0041 |
| mm31f | he | direct | raw_co | 3 | 0 | 70.12 | 89.83 ± 1.54 | 0.0040 |
| mm31f | he | syntax | agent | 3 | 0 | 85.37 | 98.37 ± 0.35 | 0.0028 |
| mm31f | he | syntax | agent15 | 3 | 0 | 85.37 | 99.19 ± 0.35 | 0.0030 |
| mm31f | he | syntax | blind | 3 | 0 | 85.37 | 95.53 ± 0.70 | 0.0044 |
| mm31f | he | syntax | hint | 3 | 0 | 85.37 | 99.39 ± 0.00 | 0.0031 |
| mm31f | he | syntax | rag | 3 | 0 | 85.37 | 98.98 ± 0.35 | 0.0032 |
| mm31f | he | syntax | rag2 | 3 | 0 | 85.37 | 99.19 ± 0.35 | 0.0031 |
| mm31f | he | syntax | raw | 3 | 0 | 85.37 | 98.78 ± 1.06 | 0.0033 |
| mm31f | or | direct | agent | 3 | 0 | 63.33 | 88.89 ± 1.92 | 0.0040 |
| mm31f | or | direct | agent15 | 3 | 0 | 63.33 | 95.56 ± 1.93 | 0.0050 |
| mm31f | or | direct | blind | 3 | 0 | 63.33 | 87.78 ± 3.85 | 0.0091 |
| mm31f | or | direct | hint | 3 | 0 | 63.33 | 97.78 ± 1.92 | 0.0048 |
| mm31f | or | direct | rag | 3 | 0 | 63.33 | 96.67 ± 0.00 | 0.0049 |
| mm31f | or | direct | rag2 | 3 | 0 | 63.33 | 96.67 ± 0.00 | 0.0057 |
| mm31f | or | direct | raw | 3 | 0 | 63.33 | 96.67 ± 0.00 | 0.0045 |
| mm31f | or | syntax | agent | 3 | 0 | 80.00 | 96.67 ± 0.00 | 0.0033 |
| mm31f | or | syntax | agent15 | 3 | 0 | 80.00 | 96.67 ± 0.00 | 0.0041 |
| mm31f | or | syntax | blind | 3 | 0 | 80.00 | 95.56 ± 1.93 | 0.0050 |
| mm31f | or | syntax | hint | 3 | 0 | 80.00 | 96.67 ± 0.00 | 0.0044 |
| mm31f | or | syntax | rag | 3 | 0 | 80.00 | 97.78 ± 1.92 | 0.0040 |
| mm31f | or | syntax | rag2 | 3 | 0 | 80.00 | 96.67 ± 0.00 | 0.0043 |
| mm31f | or | syntax | raw | 3 | 0 | 80.00 | 96.67 ± 0.00 | 0.0044 |
| u2f | ce | direct | agent | 3 | 0 | 14.29 | 65.08 ± 3.83 | 0.0197 |
| u2f | ce | direct | agent15 | 3 | 0 | 14.29 | 78.57 ± 2.38 | 0.0354 |
| u2f | ce | direct | blind | 3 | 0 | 14.29 | 31.74 ± 3.64 | 0.0739 |
| u2f | ce | direct | hint | 3 | 0 | 14.29 | 67.86 ± 3.15 | 0.0268 |
| u2f | ce | direct | rag | 3 | 0 | 14.29 | 64.29 ± 2.06 | 0.0317 |
| u2f | ce | direct | rag2 | 3 | 0 | 14.29 | 65.08 ± 4.82 | 0.0311 |
| u2f | ce | direct | raw | 3 | 0 | 14.29 | 67.86 ± 4.29 | 0.0280 |
| u2f | ce | syntax | agent | 3 | 0 | 23.81 | 66.27 ± 0.69 | 0.0209 |
| u2f | ce | syntax | agent15 | 3 | 0 | 23.81 | 74.60 ± 4.18 | 0.0401 |
| u2f | ce | syntax | blind | 3 | 0 | 23.81 | 49.21 ± 1.82 | 0.0389 |
| u2f | ce | syntax | hint | 3 | 0 | 23.81 | 69.45 ± 3.44 | 0.0287 |
| u2f | ce | syntax | rag | 3 | 0 | 23.81 | 67.86 ± 4.29 | 0.0301 |
| u2f | ce | syntax | rag2 | 3 | 0 | 23.81 | 65.88 ± 2.48 | 0.0339 |
| u2f | ce | syntax | raw | 3 | 0 | 23.81 | 66.67 ± 2.06 | 0.0292 |
| u2f | he | direct | agent | 3 | 0 | 46.34 | 96.95 ± 1.22 | 0.0019 |
| u2f | he | direct | agent15 | 3 | 0 | 46.34 | 99.80 ± 0.35 | 0.0023 |
| u2f | he | direct | blind | 3 | 0 | 45.73 | 89.63 ± 1.22 | 0.0047 |
| u2f | he | direct | hint | 3 | 0 | 46.34 | 98.17 ± 0.61 | 0.0023 |
| u2f | he | direct | hint_co | 3 | 0 | 46.34 | 60.57 ± 0.70 | 0.0024 |
| u2f | he | direct | rag | 3 | 0 | 45.73 | 98.78 ± 0.61 | 0.0026 |
| u2f | he | direct | rag2 | 3 | 0 | 46.34 | 99.39 ± 0.00 | 0.0027 |
| u2f | he | direct | rag_co | 3 | 0 | 46.34 | 59.96 ± 0.35 | 0.0025 |
| u2f | he | direct | raw | 3 | 0 | 46.34 | 98.58 ± 0.35 | 0.0025 |
| u2f | he | direct | raw_co | 3 | 0 | 46.34 | 60.17 ± 0.35 | 0.0024 |
| u2f | he | syntax | agent | 3 | 0 | 57.32 | 98.78 ± 1.22 | 0.0017 |
| u2f | he | syntax | agent15 | 3 | 0 | 57.32 | 100.00 ± 0.00 | 0.0018 |
| u2f | he | syntax | blind | 3 | 0 | 57.32 | 97.76 ± 1.41 | 0.0022 |
| u2f | he | syntax | hint | 3 | 0 | 57.32 | 98.58 ± 0.93 | 0.0018 |
| u2f | he | syntax | rag | 3 | 0 | 57.32 | 99.80 ± 0.35 | 0.0020 |
| u2f | he | syntax | rag2 | 3 | 0 | 57.32 | 98.98 ± 0.70 | 0.0021 |
| u2f | he | syntax | raw | 3 | 0 | 57.32 | 99.39 ± 1.06 | 0.0019 |
| u2f | or | direct | agent | 3 | 0 | 36.67 | 96.67 ± 0.00 | 0.0018 |
| u2f | or | direct | agent15 | 3 | 0 | 36.67 | 100.00 ± 0.00 | 0.0016 |
| u2f | or | direct | blind | 3 | 0 | 36.67 | 86.67 ± 3.34 | 0.0068 |
| u2f | or | direct | hint | 3 | 0 | 36.67 | 98.89 ± 1.92 | 0.0023 |
| u2f | or | direct | rag | 3 | 0 | 36.67 | 100.00 ± 0.00 | 0.0020 |
| u2f | or | direct | rag2 | 3 | 0 | 36.67 | 100.00 ± 0.00 | 0.0020 |
| u2f | or | direct | raw | 3 | 0 | 36.67 | 98.89 ± 1.92 | 0.0019 |
| u2f | or | syntax | agent | 3 | 0 | 80.00 | 100.00 ± 0.00 | 0.0015 |
| u2f | or | syntax | agent15 | 3 | 0 | 80.00 | 100.00 ± 0.00 | 0.0015 |
| u2f | or | syntax | blind | 3 | 0 | 80.00 | 97.78 ± 1.92 | 0.0020 |
| u2f | or | syntax | hint | 3 | 0 | 80.00 | 98.89 ± 1.92 | 0.0017 |
| u2f | or | syntax | rag | 3 | 0 | 80.00 | 98.89 ± 1.92 | 0.0018 |
| u2f | or | syntax | rag2 | 3 | 0 | 80.00 | 98.89 ± 1.92 | 0.0019 |
| u2f | or | syntax | raw | 3 | 0 | 80.00 | 97.78 ± 1.92 | 0.0018 |

## 族 G：推广到其他模型（186 个比较，Holm 在族内校正）

| 模型 | 数据集 | 起点 | A vs B | 题数 | 差值 [95% CI] | p | p(Holm，族内) | p(Holm，三族合并) | 差值 / p(Holm)（去掉不稳定与超时题） |
|---|---|---|---|---|---|---|---|---|---|
| doubao21l | ce | direct | hint vs raw | 84 | +13.49 [+7.54, +20.24] | <0.0001 | 0.0186 | 0.0346 | +13.25 / 0.0186 |
| doubao21l | ce | direct | rag vs raw | 84 | +10.32 [+5.16, +15.87] | 0.0008 | 0.1288 | 0.2416 | +10.04 / 0.1127 |
| doubao21l | ce | direct | rag vs hint | 84 | -3.17 [-9.92, +3.57] | 0.4126 | 1.0000 | 1.0000 | -3.21 / 1.0000 |
| doubao21l | ce | direct | raw vs blind | 84 | +28.17 [+19.84, +36.90] | <0.0001 | 0.0186 | 0.0346 | +27.71 / 0.0186 |
| doubao21l | ce | syntax | hint vs raw | 84 | +0.40 [-2.38, +3.57] | 1.0000 | 1.0000 | 1.0000 | +0.80 / 1.0000 |
| doubao21l | ce | syntax | rag vs raw | 84 | -1.98 [-5.95, +2.38] | 0.4679 | 1.0000 | 1.0000 | -1.20 / 1.0000 |
| doubao21l | ce | syntax | rag vs hint | 84 | -2.38 [-6.35, +1.59] | 0.3616 | 1.0000 | 1.0000 | -2.01 / 1.0000 |
| doubao21l | ce | syntax | raw vs blind | 84 | +19.44 [+13.10, +26.19] | <0.0001 | 0.0186 | 0.0346 | +18.88 / 0.0186 |
| doubao21l | he | direct | hint vs raw | 164 | +9.76 [+6.10, +13.82] | <0.0001 | 0.0186 | 0.0346 | +9.82 / 0.0186 |
| doubao21l | he | direct | rag vs raw | 164 | +7.72 [+4.47, +10.98] | <0.0001 | 0.0186 | 0.0346 | +7.36 / 0.0186 |
| doubao21l | he | direct | rag vs hint | 164 | -2.03 [-5.49, +1.02] | 0.2899 | 1.0000 | 1.0000 | -2.45 / 1.0000 |
| doubao21l | he | direct | raw vs blind | 164 | +33.54 [+27.44, +39.63] | <0.0001 | 0.0186 | 0.0346 | +33.95 / 0.0186 |
| doubao21l | he | direct | hint_co vs raw_co | 164 | +9.35 [+5.69, +13.41] | <0.0001 | 0.0186 | 0.0346 | +9.41 / 0.0186 |
| doubao21l | he | direct | rag_co vs raw_co | 164 | +6.30 [+2.64, +9.96] | 0.0010 | 0.1590 | 0.3000 | +6.13 / 0.2385 |
| doubao21l | he | syntax | hint vs raw | 164 | +0.81 [-0.20, +2.03] | 0.3082 | 1.0000 | 1.0000 | +0.82 / 1.0000 |
| doubao21l | he | syntax | rag vs raw | 164 | +1.83 [+0.41, +3.66] | 0.0435 | 1.0000 | 1.0000 | +1.84 / 1.0000 |
| doubao21l | he | syntax | rag vs hint | 164 | +1.02 [-0.20, +2.44] | 0.2832 | 1.0000 | 1.0000 | +1.02 / 1.0000 |
| doubao21l | he | syntax | raw vs blind | 164 | +4.07 [+1.63, +6.91] | 0.0017 | 0.2686 | 0.5065 | +4.09 / 0.2385 |
| doubao21l | or | direct | hint vs raw | 30 | +16.67 [+5.56, +28.89] | 0.0151 | 1.0000 | 1.0000 | +16.67 / 1.0000 |
| doubao21l | or | direct | rag vs raw | 30 | +5.56 [+1.11, +11.11] | 0.1275 | 1.0000 | 1.0000 | +5.56 / 1.0000 |
| doubao21l | or | direct | rag vs hint | 30 | -11.11 [-24.44, -0.00] | 0.1289 | 1.0000 | 1.0000 | -11.11 / 1.0000 |
| doubao21l | or | direct | raw vs blind | 30 | +23.33 [+11.11, +36.67] | 0.0008 | 0.1288 | 0.2416 | +23.33 / 0.1280 |
| doubao21l | or | syntax | hint vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| doubao21l | or | syntax | rag vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| doubao21l | or | syntax | rag vs hint | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| doubao21l | or | syntax | raw vs blind | 30 | +2.22 [+0.00, +5.56] | 0.5048 | 1.0000 | 1.0000 | +2.22 / 1.0000 |
| ds_v41f | ce | syntax | hint vs raw | 84 | +2.38 [-0.79, +5.95] | 0.2795 | 1.0000 | 1.0000 | +2.41 / 1.0000 |
| ds_v41f | ce | syntax | rag vs raw | 84 | +0.79 [-3.17, +4.76] | 0.8504 | 1.0000 | 1.0000 | +0.80 / 1.0000 |
| ds_v41f | ce | syntax | rag vs hint | 84 | -1.59 [-5.16, +1.98] | 0.5303 | 1.0000 | 1.0000 | -1.61 / 1.0000 |
| ds_v41f | ce | syntax | raw vs blind | 84 | +19.84 [+12.30, +27.78] | <0.0001 | 0.0186 | 0.0346 | +19.68 / 0.0186 |
| glm53f | ce | direct | hint vs raw | 84 | +2.78 [-1.59, +7.54] | 0.3271 | 1.0000 | 1.0000 | +2.44 / 1.0000 |
| glm53f | ce | direct | rag vs raw | 84 | +1.19 [-3.97, +6.35] | 0.7676 | 1.0000 | 1.0000 | +1.96 / 1.0000 |
| glm53f | ce | direct | rag vs hint | 84 | -1.59 [-6.75, +3.57] | 0.6631 | 1.0000 | 1.0000 | +1.96 / 1.0000 |
| glm53f | ce | direct | raw vs blind | 84 | +42.86 [+33.73, +52.38] | <0.0001 | 0.0186 | 0.0346 | +43.37 / 0.0186 |
| glm53f | ce | syntax | hint vs raw | 84 | -0.79 [-4.37, +3.17] | 0.8337 | 1.0000 | 1.0000 | -0.42 / 1.0000 |
| glm53f | ce | syntax | rag vs raw | 84 | -3.97 [-8.33, +0.40] | 0.1105 | 1.0000 | 1.0000 | -0.88 / 1.0000 |
| glm53f | ce | syntax | rag vs hint | 84 | -3.17 [-8.33, +1.59] | 0.2726 | 1.0000 | 1.0000 | -1.69 / 1.0000 |
| glm53f | ce | syntax | raw vs blind | 84 | +19.84 [+11.90, +27.78] | <0.0001 | 0.0186 | 0.0346 | +18.99 / 0.0186 |
| glm53f | he | direct | hint vs raw | 164 | +0.41 [+0.00, +1.02] | 0.4988 | 1.0000 | 1.0000 | +0.21 / 1.0000 |
| glm53f | he | direct | rag vs raw | 164 | -0.20 [-1.02, +0.41] | 1.0000 | 1.0000 | 1.0000 | -0.20 / 1.0000 |
| glm53f | he | direct | rag vs hint | 164 | -0.61 [-1.63, +0.00] | 0.5059 | 1.0000 | 1.0000 | -0.21 / 1.0000 |
| glm53f | he | direct | raw vs blind | 164 | +8.74 [+5.28, +12.60] | <0.0001 | 0.0186 | 0.0346 | +8.79 / 0.0186 |
| glm53f | he | direct | hint_co vs raw_co | 164 | +0.00 [-1.42, +1.83] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| glm53f | he | direct | rag_co vs raw_co | 164 | -0.41 [-1.83, +1.22] | 0.8408 | 1.0000 | 1.0000 | -0.41 / 1.0000 |
| glm53f | he | syntax | hint vs raw | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| glm53f | he | syntax | rag vs raw | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| glm53f | he | syntax | rag vs hint | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| glm53f | he | syntax | raw vs blind | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| glm53f | or | direct | hint vs raw | 30 | -1.11 [-3.33, +0.00] | 1.0000 | 1.0000 | 1.0000 | -1.11 / 1.0000 |
| glm53f | or | direct | rag vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| glm53f | or | direct | rag vs hint | 30 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 | 1.0000 | +1.11 / 1.0000 |
| glm53f | or | direct | raw vs blind | 30 | +17.78 [+7.78, +28.89] | 0.0041 | 0.6436 | 1.0000 | +17.78 / 0.6436 |
| glm53f | or | syntax | hint vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| glm53f | or | syntax | rag vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| glm53f | or | syntax | rag vs hint | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| glm53f | or | syntax | raw vs blind | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| gpt6l | ce | direct | hint vs raw | 84 | +0.00 [-2.78, +2.38] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| gpt6l | ce | direct | rag vs raw | 84 | +2.38 [-1.59, +7.14] | 0.3951 | 1.0000 | 1.0000 | +2.41 / 1.0000 |
| gpt6l | ce | direct | rag vs hint | 84 | +2.38 [-1.59, +6.75] | 0.3740 | 1.0000 | 1.0000 | +2.41 / 1.0000 |
| gpt6l | ce | direct | raw vs blind | 84 | +22.22 [+14.68, +30.16] | <0.0001 | 0.0186 | 0.0346 | +22.09 / 0.0186 |
| gpt6l | ce | syntax | hint vs raw | 84 | -0.00 [-3.57, +3.17] | 1.0000 | 1.0000 | 1.0000 | -0.00 / 1.0000 |
| gpt6l | ce | syntax | rag vs raw | 84 | +0.00 [-3.17, +2.78] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| gpt6l | ce | syntax | rag vs hint | 84 | -0.00 [-3.97, +3.97] | 1.0000 | 1.0000 | 1.0000 | -0.00 / 1.0000 |
| gpt6l | ce | syntax | raw vs blind | 84 | +21.43 [+13.10, +30.56] | <0.0001 | 0.0186 | 0.0346 | +21.69 / 0.0186 |
| gpt6l | he | direct | hint vs raw | 164 | +1.42 [+0.20, +3.05] | 0.0975 | 1.0000 | 1.0000 | +1.43 / 1.0000 |
| gpt6l | he | direct | rag vs raw | 164 | +0.41 [-1.02, +1.83] | 0.8046 | 1.0000 | 1.0000 | +0.41 / 1.0000 |
| gpt6l | he | direct | rag vs hint | 164 | -1.02 [-2.03, +0.00] | 0.1280 | 1.0000 | 1.0000 | -1.02 / 1.0000 |
| gpt6l | he | direct | raw vs blind | 164 | +15.65 [+10.37, +21.34] | <0.0001 | 0.0186 | 0.0346 | +15.75 / 0.0186 |
| gpt6l | he | direct | hint_co vs raw_co | 164 | +1.22 [+0.20, +2.64] | 0.1283 | 1.0000 | 1.0000 | +1.23 / 1.0000 |
| gpt6l | he | direct | rag_co vs raw_co | 164 | +0.20 [-1.63, +2.24] | 1.0000 | 1.0000 | 1.0000 | +0.20 / 1.0000 |
| gpt6l | he | syntax | hint vs raw | 164 | -1.22 [-3.25, +0.20] | 0.3691 | 1.0000 | 1.0000 | -1.23 / 1.0000 |
| gpt6l | he | syntax | rag vs raw | 164 | +0.00 [-0.61, +0.61] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| gpt6l | he | syntax | rag vs hint | 164 | +1.22 [+0.00, +3.05] | 0.4984 | 1.0000 | 1.0000 | +1.23 / 1.0000 |
| gpt6l | he | syntax | raw vs blind | 164 | +3.66 [+1.42, +6.50] | 0.0085 | 1.0000 | 1.0000 | +3.68 / 1.0000 |
| gpt6l | or | direct | hint vs raw | 30 | +2.22 [+0.00, +6.67] | 1.0000 | 1.0000 | 1.0000 | +2.22 / 1.0000 |
| gpt6l | or | direct | rag vs raw | 30 | +2.22 [+0.00, +6.67] | 1.0000 | 1.0000 | 1.0000 | +2.22 / 1.0000 |
| gpt6l | or | direct | rag vs hint | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| gpt6l | or | direct | raw vs blind | 30 | +23.33 [+10.00, +38.89] | 0.0065 | 1.0000 | 1.0000 | +23.33 / 1.0000 |
| gpt6l | or | syntax | hint vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| gpt6l | or | syntax | rag vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| gpt6l | or | syntax | rag vs hint | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| gpt6l | or | syntax | raw vs blind | 30 | +3.33 [+0.00, +10.00] | 1.0000 | 1.0000 | 1.0000 | +3.33 / 1.0000 |
| haiku55 | ce | direct | hint vs raw | 84 | +0.79 [-2.38, +3.57] | 0.7929 | 1.0000 | 1.0000 | +0.80 / 1.0000 |
| haiku55 | ce | direct | rag vs raw | 84 | +0.00 [-3.17, +2.78] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | ce | direct | rag vs hint | 84 | -0.79 [-3.57, +1.59] | 0.7743 | 1.0000 | 1.0000 | -0.80 / 1.0000 |
| haiku55 | ce | direct | raw vs blind | 84 | +29.76 [+21.43, +38.49] | <0.0001 | 0.0186 | 0.0346 | +29.32 / 0.0186 |
| haiku55 | ce | syntax | hint vs raw | 84 | -0.40 [-2.78, +2.38] | 1.0000 | 1.0000 | 1.0000 | -0.40 / 1.0000 |
| haiku55 | ce | syntax | rag vs raw | 84 | -0.79 [-2.78, +1.19] | 0.6834 | 1.0000 | 1.0000 | -0.80 / 1.0000 |
| haiku55 | ce | syntax | rag vs hint | 84 | -0.40 [-3.17, +2.38] | 1.0000 | 1.0000 | 1.0000 | -0.40 / 1.0000 |
| haiku55 | ce | syntax | raw vs blind | 84 | +14.68 [+8.33, +21.43] | <0.0001 | 0.0186 | 0.0346 | +14.86 / 0.0186 |
| haiku55 | he | direct | hint vs raw | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | he | direct | rag vs raw | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | he | direct | rag vs hint | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | he | direct | raw vs blind | 164 | +7.32 [+4.27, +10.98] | <0.0001 | 0.0186 | 0.0346 | +7.16 / 0.0186 |
| haiku55 | he | direct | hint_co vs raw_co | 164 | +0.41 [+0.00, +1.02] | 0.5026 | 1.0000 | 1.0000 | +0.41 / 1.0000 |
| haiku55 | he | direct | rag_co vs raw_co | 164 | +0.20 [-0.41, +1.02] | 1.0000 | 1.0000 | 1.0000 | +0.20 / 1.0000 |
| haiku55 | he | syntax | hint vs raw | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | he | syntax | rag vs raw | 164 | -0.20 [-0.61, +0.00] | 1.0000 | 1.0000 | 1.0000 | -0.20 / 1.0000 |
| haiku55 | he | syntax | rag vs hint | 164 | -0.20 [-0.61, +0.00] | 1.0000 | 1.0000 | 1.0000 | -0.20 / 1.0000 |
| haiku55 | he | syntax | raw vs blind | 164 | +0.81 [+0.00, +2.24] | 0.4953 | 1.0000 | 1.0000 | +0.82 / 1.0000 |
| haiku55 | or | direct | hint vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | or | direct | rag vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | or | direct | rag vs hint | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | or | direct | raw vs blind | 30 | +10.00 [+2.22, +20.00] | 0.0630 | 1.0000 | 1.0000 | +10.00 / 1.0000 |
| haiku55 | or | syntax | hint vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | or | syntax | rag vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | or | syntax | rag vs hint | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | or | syntax | raw vs blind | 30 | +2.22 [+0.00, +5.56] | 0.5043 | 1.0000 | 1.0000 | +2.22 / 1.0000 |
| kimik31p | ce | direct | hint vs raw | 84 | +1.19 [-1.59, +3.97] | 0.5854 | 1.0000 | 1.0000 | +1.20 / 1.0000 |
| kimik31p | ce | direct | rag vs raw | 84 | +2.78 [-0.40, +6.75] | 0.2213 | 1.0000 | 1.0000 | +2.81 / 1.0000 |
| kimik31p | ce | direct | rag vs hint | 84 | +1.59 [-1.98, +5.56] | 0.5626 | 1.0000 | 1.0000 | +1.61 / 1.0000 |
| kimik31p | ce | direct | raw vs blind | 84 | +20.63 [+13.49, +28.17] | <0.0001 | 0.0186 | 0.0346 | +20.88 / 0.0186 |
| kimik31p | ce | syntax | hint vs raw | 84 | +1.59 [-1.19, +4.76] | 0.4701 | 1.0000 | 1.0000 | +1.61 / 1.0000 |
| kimik31p | ce | syntax | rag vs raw | 84 | +0.79 [-2.38, +3.97] | 0.8092 | 1.0000 | 1.0000 | +0.80 / 1.0000 |
| kimik31p | ce | syntax | rag vs hint | 84 | -0.79 [-3.97, +2.38] | 0.8123 | 1.0000 | 1.0000 | -0.80 / 1.0000 |
| kimik31p | ce | syntax | raw vs blind | 84 | +21.43 [+13.89, +29.37] | <0.0001 | 0.0186 | 0.0346 | +21.69 / 0.0186 |
| kimik31p | he | direct | hint vs raw | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | he | direct | rag vs raw | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | he | direct | rag vs hint | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | he | direct | raw vs blind | 164 | +0.61 [+0.00, +1.63] | 0.4998 | 1.0000 | 1.0000 | +0.61 / 1.0000 |
| kimik31p | he | direct | hint_co vs raw_co | 164 | +0.41 [-0.41, +1.42] | 0.7503 | 1.0000 | 1.0000 | +0.41 / 1.0000 |
| kimik31p | he | direct | rag_co vs raw_co | 164 | +0.61 [-0.41, +2.03] | 0.5080 | 1.0000 | 1.0000 | +0.61 / 1.0000 |
| kimik31p | he | syntax | hint vs raw | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | he | syntax | rag vs raw | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | he | syntax | rag vs hint | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | he | syntax | raw vs blind | 164 | +0.41 [+0.00, +1.22] | 1.0000 | 1.0000 | 1.0000 | +0.41 / 1.0000 |
| kimik31p | or | direct | hint vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | or | direct | rag vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | or | direct | rag vs hint | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | or | direct | raw vs blind | 30 | +4.44 [+0.00, +11.11] | 0.5052 | 1.0000 | 1.0000 | +4.44 / 1.0000 |
| kimik31p | or | syntax | hint vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | or | syntax | rag vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | or | syntax | rag vs hint | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | or | syntax | raw vs blind | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| mm31f | ce | direct | hint vs raw | 84 | +0.00 [-2.78, +2.78] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| mm31f | ce | direct | rag vs raw | 84 | -3.17 [-7.54, +1.19] | 0.2424 | 1.0000 | 1.0000 | -3.21 / 1.0000 |
| mm31f | ce | direct | rag vs hint | 84 | -3.17 [-7.14, +1.19] | 0.2077 | 1.0000 | 1.0000 | -3.21 / 1.0000 |
| mm31f | ce | direct | raw vs blind | 84 | +19.44 [+12.70, +26.98] | <0.0001 | 0.0186 | 0.0346 | +19.68 / 0.0186 |
| mm31f | ce | syntax | hint vs raw | 84 | -0.40 [-4.37, +3.17] | 1.0000 | 1.0000 | 1.0000 | -0.40 / 1.0000 |
| mm31f | ce | syntax | rag vs raw | 84 | +0.00 [-4.76, +4.76] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| mm31f | ce | syntax | rag vs hint | 84 | +0.40 [-2.38, +3.57] | 1.0000 | 1.0000 | 1.0000 | +0.40 / 1.0000 |
| mm31f | ce | syntax | raw vs blind | 84 | +15.87 [+9.13, +23.02] | <0.0001 | 0.0186 | 0.0346 | +16.06 / 0.0186 |
| mm31f | he | direct | hint vs raw | 164 | +1.22 [+0.00, +2.64] | 0.1100 | 1.0000 | 1.0000 | +1.23 / 1.0000 |
| mm31f | he | direct | rag vs raw | 164 | +2.03 [+0.61, +3.66] | 0.0156 | 1.0000 | 1.0000 | +2.04 / 1.0000 |
| mm31f | he | direct | rag vs hint | 164 | +0.81 [+0.00, +2.24] | 0.4945 | 1.0000 | 1.0000 | +0.82 / 1.0000 |
| mm31f | he | direct | raw vs blind | 164 | +5.28 [+2.44, +8.54] | 0.0006 | 0.0972 | 0.1836 | +5.32 / 0.0810 |
| mm31f | he | direct | hint_co vs raw_co | 164 | +1.63 [+0.20, +3.46] | 0.0907 | 1.0000 | 1.0000 | +1.64 / 1.0000 |
| mm31f | he | direct | rag_co vs raw_co | 164 | +2.64 [+0.81, +4.47] | 0.0086 | 1.0000 | 1.0000 | +2.66 / 1.0000 |
| mm31f | he | syntax | hint vs raw | 164 | +0.61 [+0.00, +1.42] | 0.2480 | 1.0000 | 1.0000 | +0.61 / 1.0000 |
| mm31f | he | syntax | rag vs raw | 164 | +0.20 [+0.00, +0.61] | 1.0000 | 1.0000 | 1.0000 | +0.20 / 1.0000 |
| mm31f | he | syntax | rag vs hint | 164 | -0.41 [-1.02, +0.00] | 0.4963 | 1.0000 | 1.0000 | -0.41 / 1.0000 |
| mm31f | he | syntax | raw vs blind | 164 | +3.25 [+1.02, +5.89] | 0.0159 | 1.0000 | 1.0000 | +3.27 / 1.0000 |
| mm31f | or | direct | hint vs raw | 30 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 | 1.0000 | +1.11 / 1.0000 |
| mm31f | or | direct | rag vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| mm31f | or | direct | rag vs hint | 30 | -1.11 [-3.33, +0.00] | 1.0000 | 1.0000 | 1.0000 | -1.11 / 1.0000 |
| mm31f | or | direct | raw vs blind | 30 | +8.89 [+1.11, +18.89] | 0.1299 | 1.0000 | 1.0000 | +8.89 / 1.0000 |
| mm31f | or | syntax | hint vs raw | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| mm31f | or | syntax | rag vs raw | 30 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 | 1.0000 | +1.11 / 1.0000 |
| mm31f | or | syntax | rag vs hint | 30 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 | 1.0000 | +1.11 / 1.0000 |
| mm31f | or | syntax | raw vs blind | 30 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 | 1.0000 | +1.11 / 1.0000 |
| u2f | ce | direct | hint vs raw | 84 | -0.00 [-5.95, +5.56] | 1.0000 | 1.0000 | 1.0000 | -0.00 / 1.0000 |
| u2f | ce | direct | rag vs raw | 84 | -3.57 [-8.33, +0.79] | 0.1812 | 1.0000 | 1.0000 | -3.21 / 1.0000 |
| u2f | ce | direct | rag vs hint | 84 | -3.57 [-8.33, +0.79] | 0.1722 | 1.0000 | 1.0000 | -3.21 / 1.0000 |
| u2f | ce | direct | raw vs blind | 84 | +36.11 [+27.78, +44.84] | <0.0001 | 0.0186 | 0.0346 | +36.14 / 0.0186 |
| u2f | ce | syntax | hint vs raw | 84 | +2.78 [-1.19, +7.14] | 0.2679 | 1.0000 | 1.0000 | +3.21 / 1.0000 |
| u2f | ce | syntax | rag vs raw | 84 | +1.19 [-2.78, +5.16] | 0.6958 | 1.0000 | 1.0000 | +1.61 / 1.0000 |
| u2f | ce | syntax | rag vs hint | 84 | -1.59 [-4.76, +1.59] | 0.4562 | 1.0000 | 1.0000 | -1.61 / 1.0000 |
| u2f | ce | syntax | raw vs blind | 84 | +17.46 [+10.32, +24.60] | <0.0001 | 0.0186 | 0.0346 | +17.27 / 0.0186 |
| u2f | he | direct | hint vs raw | 164 | -0.41 [-1.83, +0.81] | 0.7618 | 1.0000 | 1.0000 | -0.41 / 1.0000 |
| u2f | he | direct | rag vs raw | 164 | +0.20 [-1.22, +1.42] | 1.0000 | 1.0000 | 1.0000 | +0.20 / 1.0000 |
| u2f | he | direct | rag vs hint | 164 | +0.61 [-1.02, +2.24] | 0.6140 | 1.0000 | 1.0000 | +0.61 / 1.0000 |
| u2f | he | direct | raw vs blind | 164 | +8.94 [+5.89, +12.40] | <0.0001 | 0.0186 | 0.0346 | +9.00 / 0.0186 |
| u2f | he | direct | hint_co vs raw_co | 164 | +0.41 [-1.42, +2.24] | 0.8296 | 1.0000 | 1.0000 | +0.41 / 1.0000 |
| u2f | he | direct | rag_co vs raw_co | 164 | -0.20 [-1.83, +1.42] | 1.0000 | 1.0000 | 1.0000 | -0.20 / 1.0000 |
| u2f | he | syntax | hint vs raw | 164 | -0.81 [-2.03, +0.20] | 0.3231 | 1.0000 | 1.0000 | -0.82 / 1.0000 |
| u2f | he | syntax | rag vs raw | 164 | +0.41 [+0.00, +1.02] | 0.5007 | 1.0000 | 1.0000 | +0.41 / 1.0000 |
| u2f | he | syntax | rag vs hint | 164 | +1.22 [+0.20, +2.44] | 0.0654 | 1.0000 | 1.0000 | +1.23 / 1.0000 |
| u2f | he | syntax | raw vs blind | 164 | +1.63 [+0.20, +3.25] | 0.0544 | 1.0000 | 1.0000 | +1.64 / 1.0000 |
| u2f | or | direct | hint vs raw | 30 | +0.00 [-3.33, +3.33] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| u2f | or | direct | rag vs raw | 30 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 | 1.0000 | +1.11 / 1.0000 |
| u2f | or | direct | rag vs hint | 30 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 | 1.0000 | +1.11 / 1.0000 |
| u2f | or | direct | raw vs blind | 30 | +12.22 [+5.56, +20.00] | 0.0079 | 1.0000 | 1.0000 | +12.22 / 1.0000 |
| u2f | or | syntax | hint vs raw | 30 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 | 1.0000 | +1.11 / 1.0000 |
| u2f | or | syntax | rag vs raw | 30 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 | 1.0000 | +1.11 / 1.0000 |
| u2f | or | syntax | rag vs hint | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| u2f | or | syntax | raw vs blind | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |

## 族 A：Agent 基线（107 个比较，Holm 在族内校正）

| 模型 | 数据集 | 起点 | A vs B | 题数 | 差值 [95% CI] | p | p(Holm，族内) | p(Holm，三族合并) | 差值 / p(Holm)（去掉不稳定与超时题） |
|---|---|---|---|---|---|---|---|---|---|
| doubao21l | ce | direct | agent vs rag | 84 | -10.32 [-15.87, -4.76] | 0.0006 | 0.0546 | 0.1836 | -9.64 / 0.0990 |
| doubao21l | ce | direct | agent15 vs agent | 84 | +25.79 [+17.86, +33.73] | <0.0001 | 0.0107 | 0.0346 | +25.30 / 0.0107 |
| doubao21l | ce | syntax | agent vs rag | 84 | +2.38 [-1.98, +6.75] | 0.3881 | 1.0000 | 1.0000 | +1.61 / 1.0000 |
| doubao21l | ce | syntax | agent15 vs agent | 84 | +11.11 [+5.16, +17.46] | 0.0007 | 0.0623 | 0.2121 | +10.84 / 0.1157 |
| doubao21l | he | direct | agent vs rag | 164 | -9.55 [-13.82, -5.28] | 0.0002 | 0.0196 | 0.0626 | -9.20 / 0.0107 |
| doubao21l | he | direct | agent15 vs agent | 164 | +15.24 [+10.77, +20.12] | <0.0001 | 0.0107 | 0.0346 | +14.72 / 0.0107 |
| doubao21l | he | syntax | agent vs rag | 164 | -1.42 [-3.46, +0.41] | 0.2144 | 1.0000 | 1.0000 | -1.43 / 1.0000 |
| doubao21l | he | syntax | agent15 vs agent | 164 | +2.44 [+0.81, +4.47] | 0.0145 | 1.0000 | 1.0000 | +2.45 / 1.0000 |
| doubao21l | or | direct | agent vs rag | 30 | -5.56 [-11.11, -1.11] | 0.1300 | 1.0000 | 1.0000 | -5.56 / 1.0000 |
| doubao21l | or | direct | agent15 vs agent | 30 | +14.44 [+4.44, +26.67] | 0.0324 | 1.0000 | 1.0000 | +14.44 / 1.0000 |
| doubao21l | or | syntax | agent vs rag | 30 | -1.11 [-3.33, +0.00] | 1.0000 | 1.0000 | 1.0000 | -1.11 / 1.0000 |
| doubao21l | or | syntax | agent15 vs agent | 30 | +2.22 [+0.00, +5.56] | 0.4991 | 1.0000 | 1.0000 | +2.22 / 1.0000 |
| doubao_mini | ce | direct | agent vs rag | 84 | -7.14 [-12.70, -2.38] | 0.0091 | 0.7552 | 1.0000 | -7.23 / 0.8216 |
| doubao_mini | ce | direct | agent15 vs agent | 84 | +8.73 [+4.37, +13.89] | 0.0003 | 0.0285 | 0.0930 | +8.84 / 0.0282 |
| doubao_mini | ce | syntax | agent vs rag | 84 | -7.14 [-12.30, -2.78] | 0.0052 | 0.4420 | 1.0000 | -7.23 / 0.4128 |
| doubao_mini | ce | syntax | agent15 vs agent | 84 | +7.94 [+3.57, +13.10] | 0.0021 | 0.1827 | 0.6236 | +8.03 / 0.1653 |
| doubao_mini | he | direct | agent vs rag | 164 | -10.37 [-15.24, -5.69] | <0.0001 | 0.0107 | 0.0346 | -10.22 / 0.0107 |
| doubao_mini | he | direct | agent15 vs agent | 164 | +23.17 [+18.09, +28.46] | <0.0001 | 0.0107 | 0.0346 | +22.90 / 0.0107 |
| doubao_mini | he | syntax | agent vs rag | 164 | -5.28 [-9.15, -1.83] | 0.0068 | 0.5711 | 1.0000 | -5.32 / 0.6551 |
| doubao_mini | he | syntax | agent15 vs agent | 164 | +6.50 [+3.86, +9.55] | <0.0001 | 0.0107 | 0.0346 | +6.54 / 0.0107 |
| doubao_mini | or | direct | agent vs rag | 30 | -7.78 [-15.56, -0.00] | 0.0909 | 1.0000 | 1.0000 | -7.78 / 1.0000 |
| doubao_mini | or | direct | agent15 vs agent | 30 | +31.11 [+17.78, +45.56] | 0.0002 | 0.0196 | 0.0626 | +31.11 / 0.0194 |
| doubao_mini | or | syntax | agent vs rag | 30 | -6.67 [-15.56, +1.11] | 0.2508 | 1.0000 | 1.0000 | -6.67 / 1.0000 |
| doubao_mini | or | syntax | agent15 vs agent | 30 | +8.89 [+0.00, +18.89] | 0.1548 | 1.0000 | 1.0000 | +8.89 / 1.0000 |
| ds_v41f | ce | direct | agent vs rag | 84 | -4.76 [-8.33, -1.59] | 0.0106 | 0.8691 | 1.0000 | -4.42 / 1.0000 |
| ds_v41f | ce | direct | agent15 vs agent | 84 | +8.73 [+4.37, +13.49] | 0.0004 | 0.0376 | 0.1236 | +8.43 / 0.0728 |
| ds_v41f | ce | syntax | agent vs rag | 84 | -3.17 [-7.14, +0.00] | 0.1389 | 1.0000 | 1.0000 | -3.21 / 1.0000 |
| ds_v41f | ce | syntax | agent15 vs agent | 84 | +9.92 [+5.16, +15.08] | 0.0004 | 0.0376 | 0.1236 | +9.64 / 0.0372 |
| ds_v41f | he | direct | agent vs rag | 164 | -0.81 [-1.83, +0.00] | 0.2463 | 1.0000 | 1.0000 | -0.82 / 1.0000 |
| ds_v41f | he | direct | agent15 vs agent | 164 | +1.02 [+0.20, +2.24] | 0.1199 | 1.0000 | 1.0000 | +1.02 / 1.0000 |
| ds_v41f | he | syntax | agent vs rag | 164 | -0.61 [-1.83, +0.00] | 1.0000 | 1.0000 | 1.0000 | -0.61 / 1.0000 |
| ds_v41f | he | syntax | agent15 vs agent | 164 | +0.61 [+0.00, +1.83] | 1.0000 | 1.0000 | 1.0000 | +0.61 / 1.0000 |
| ds_v41f | or | direct | agent vs rag | 30 | -1.11 [-3.33, +0.00] | 1.0000 | 1.0000 | 1.0000 | -1.11 / 1.0000 |
| ds_v41f | or | direct | agent15 vs agent | 30 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 | 1.0000 | +1.11 / 1.0000 |
| ds_v41f | or | syntax | agent vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| ds_v41f | or | syntax | agent15 vs agent | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| glm53f | ce | direct | agent vs rag | 84 | -2.38 [-6.75, +1.59] | 0.3827 | 1.0000 | 1.0000 | -2.94 / 1.0000 |
| glm53f | ce | direct | agent15 vs agent | 84 | +13.89 [+8.73, +19.44] | <0.0001 | 0.0107 | 0.0346 | +13.82 / 0.0107 |
| glm53f | ce | syntax | agent vs rag | 84 | +0.79 [-4.37, +5.95] | 0.8814 | 1.0000 | 1.0000 | -1.27 / 1.0000 |
| glm53f | he | direct | agent vs rag | 164 | +0.61 [+0.00, +1.83] | 1.0000 | 1.0000 | 1.0000 | +0.61 / 1.0000 |
| glm53f | he | direct | agent15 vs agent | 164 | +0.20 [+0.00, +0.61] | 1.0000 | 1.0000 | 1.0000 | +0.20 / 1.0000 |
| glm53f | he | syntax | agent vs rag | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| glm53f | he | syntax | agent15 vs agent | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| glm53f | or | direct | agent vs rag | 30 | -4.44 [-11.11, +0.00] | 0.5072 | 1.0000 | 1.0000 | -4.44 / 1.0000 |
| glm53f | or | direct | agent15 vs agent | 30 | +4.44 [+0.00, +11.11] | 0.5072 | 1.0000 | 1.0000 | +4.44 / 1.0000 |
| glm53f | or | syntax | agent vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| glm53f | or | syntax | agent15 vs agent | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| gpt6l | ce | direct | agent vs rag | 84 | -0.00 [-3.97, +3.97] | 1.0000 | 1.0000 | 1.0000 | -0.00 / 1.0000 |
| gpt6l | ce | direct | agent15 vs agent | 84 | +9.52 [+4.76, +15.08] | 0.0004 | 0.0376 | 0.1236 | +9.64 / 0.0194 |
| gpt6l | ce | syntax | agent vs rag | 84 | +0.79 [-2.78, +4.76] | 0.8458 | 1.0000 | 1.0000 | +0.80 / 1.0000 |
| gpt6l | ce | syntax | agent15 vs agent | 84 | +5.56 [+1.59, +10.32] | 0.0239 | 1.0000 | 1.0000 | +5.62 / 1.0000 |
| gpt6l | he | direct | agent vs rag | 164 | -1.63 [-3.46, -0.20] | 0.0924 | 1.0000 | 1.0000 | -1.64 / 1.0000 |
| gpt6l | he | direct | agent15 vs agent | 164 | +3.25 [+0.81, +5.89] | 0.0148 | 1.0000 | 1.0000 | +3.27 / 1.0000 |
| gpt6l | he | syntax | agent vs rag | 164 | -0.41 [-1.22, +0.41] | 0.6215 | 1.0000 | 1.0000 | -0.41 / 1.0000 |
| gpt6l | he | syntax | agent15 vs agent | 164 | +0.20 [-0.41, +1.02] | 1.0000 | 1.0000 | 1.0000 | +0.20 / 1.0000 |
| gpt6l | or | direct | agent vs rag | 30 | -1.11 [-3.33, +0.00] | 1.0000 | 1.0000 | 1.0000 | -1.11 / 1.0000 |
| gpt6l | or | direct | agent15 vs agent | 30 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 | 1.0000 | +1.11 / 1.0000 |
| gpt6l | or | syntax | agent vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| gpt6l | or | syntax | agent15 vs agent | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | ce | direct | agent vs rag | 84 | +1.19 [-2.78, +5.56] | 0.7274 | 1.0000 | 1.0000 | +1.20 / 1.0000 |
| haiku55 | ce | direct | agent15 vs agent | 84 | +1.98 [-1.98, +5.95] | 0.4503 | 1.0000 | 1.0000 | +1.61 / 1.0000 |
| haiku55 | ce | syntax | agent vs rag | 84 | -0.79 [-2.78, +1.19] | 0.6855 | 1.0000 | 1.0000 | -0.80 / 1.0000 |
| haiku55 | ce | syntax | agent15 vs agent | 84 | +3.17 [+0.79, +5.95] | 0.0320 | 1.0000 | 1.0000 | +3.21 / 1.0000 |
| haiku55 | he | direct | agent vs rag | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | he | direct | agent15 vs agent | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | he | syntax | agent vs rag | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | he | syntax | agent15 vs agent | 164 | +0.20 [+0.00, +0.61] | 1.0000 | 1.0000 | 1.0000 | +0.20 / 1.0000 |
| haiku55 | or | direct | agent vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | or | direct | agent15 vs agent | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | or | syntax | agent vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | or | syntax | agent15 vs agent | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | ce | direct | agent vs rag | 84 | -4.37 [-8.73, -0.40] | 0.0550 | 1.0000 | 1.0000 | -4.42 / 1.0000 |
| kimik31p | ce | direct | agent15 vs agent | 84 | +17.06 [+9.92, +24.60] | <0.0001 | 0.0107 | 0.0346 | +17.27 / 0.0107 |
| kimik31p | ce | syntax | agent vs rag | 84 | +0.00 [-4.37, +3.97] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | ce | syntax | agent15 vs agent | 84 | +11.11 [+5.95, +17.06] | <0.0001 | 0.0107 | 0.0346 | +11.24 / 0.0107 |
| kimik31p | he | direct | agent vs rag | 164 | -0.20 [-0.61, +0.00] | 1.0000 | 1.0000 | 1.0000 | -0.20 / 1.0000 |
| kimik31p | he | direct | agent15 vs agent | 164 | +0.20 [+0.00, +0.61] | 1.0000 | 1.0000 | 1.0000 | +0.20 / 1.0000 |
| kimik31p | he | syntax | agent vs rag | 164 | -0.20 [-0.61, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | he | syntax | agent15 vs agent | 164 | +0.20 [+0.00, +0.61] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | or | direct | agent vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | or | direct | agent15 vs agent | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | or | syntax | agent vs rag | 30 | -1.11 [-3.33, +0.00] | 1.0000 | 1.0000 | 1.0000 | -1.11 / 1.0000 |
| kimik31p | or | syntax | agent15 vs agent | 30 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 | 1.0000 | +1.11 / 1.0000 |
| mm31f | ce | direct | agent vs rag | 84 | -7.14 [-12.70, -2.38] | 0.0112 | 0.9071 | 1.0000 | -7.23 / 1.0000 |
| mm31f | ce | direct | agent15 vs agent | 84 | +8.73 [+4.37, +13.89] | 0.0002 | 0.0196 | 0.0626 | +8.84 / 0.0194 |
| mm31f | ce | syntax | agent vs rag | 84 | -4.37 [-8.73, -0.40] | 0.0580 | 1.0000 | 1.0000 | -4.42 / 1.0000 |
| mm31f | ce | syntax | agent15 vs agent | 84 | +4.37 [+1.19, +7.94] | 0.0164 | 1.0000 | 1.0000 | +4.42 / 1.0000 |
| mm31f | he | direct | agent vs rag | 164 | -3.05 [-5.28, -1.02] | 0.0031 | 0.2666 | 0.9175 | -3.07 / 0.4250 |
| mm31f | he | direct | agent15 vs agent | 164 | +2.24 [+0.61, +4.27] | 0.0161 | 1.0000 | 1.0000 | +2.25 / 1.0000 |
| mm31f | he | syntax | agent vs rag | 164 | -0.61 [-1.63, +0.00] | 0.5034 | 1.0000 | 1.0000 | -0.61 / 1.0000 |
| mm31f | he | syntax | agent15 vs agent | 164 | +0.81 [+0.00, +2.24] | 0.5034 | 1.0000 | 1.0000 | +0.82 / 1.0000 |
| mm31f | or | direct | agent vs rag | 30 | -7.78 [-16.67, -1.11] | 0.1299 | 1.0000 | 1.0000 | -7.78 / 1.0000 |
| mm31f | or | direct | agent15 vs agent | 30 | +6.67 [+1.11, +14.44] | 0.1299 | 1.0000 | 1.0000 | +6.67 / 1.0000 |
| mm31f | or | syntax | agent vs rag | 30 | -1.11 [-3.33, +0.00] | 1.0000 | 1.0000 | 1.0000 | -1.11 / 1.0000 |
| mm31f | or | syntax | agent15 vs agent | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| u2f | ce | direct | agent vs rag | 84 | +0.79 [-3.17, +4.76] | 0.8451 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| u2f | ce | direct | agent15 vs agent | 84 | +13.49 [+8.73, +18.65] | <0.0001 | 0.0107 | 0.0346 | +13.25 / 0.0107 |
| u2f | ce | syntax | agent vs rag | 84 | -1.59 [-5.95, +2.78] | 0.6132 | 1.0000 | 1.0000 | -2.01 / 1.0000 |
| u2f | ce | syntax | agent15 vs agent | 84 | +8.33 [+3.97, +13.10] | 0.0006 | 0.0546 | 0.1836 | +8.84 / 0.0460 |
| u2f | he | direct | agent vs rag | 164 | -1.83 [-3.46, -0.41] | 0.0330 | 1.0000 | 1.0000 | -1.84 / 1.0000 |
| u2f | he | direct | agent15 vs agent | 164 | +2.85 [+1.42, +4.67] | 0.0011 | 0.0968 | 0.3289 | +2.86 / 0.1496 |
| u2f | he | syntax | agent vs rag | 164 | -1.02 [-2.03, +0.00] | 0.1200 | 1.0000 | 1.0000 | -1.02 / 1.0000 |
| u2f | he | syntax | agent15 vs agent | 164 | +1.22 [+0.41, +2.24] | 0.0308 | 1.0000 | 1.0000 | +1.23 / 1.0000 |
| u2f | or | direct | agent vs rag | 30 | -3.33 [-10.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | -3.33 / 1.0000 |
| u2f | or | direct | agent15 vs agent | 30 | +3.33 [+0.00, +10.00] | 1.0000 | 1.0000 | 1.0000 | +3.33 / 1.0000 |
| u2f | or | syntax | agent vs rag | 30 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 | 1.0000 | +1.11 / 1.0000 |
| u2f | or | syntax | agent15 vs agent | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |

## 族 R：改进检索 rag2（53 个比较，Holm 在族内校正）

| 模型 | 数据集 | 起点 | A vs B | 题数 | 差值 [95% CI] | p | p(Holm，族内) | p(Holm，三族合并) | 差值 / p(Holm)（去掉不稳定与超时题） |
|---|---|---|---|---|---|---|---|---|---|
| doubao21l | ce | direct | rag2 vs rag | 84 | +0.79 [-3.17, +5.16] | 0.8560 | 1.0000 | 1.0000 | +0.80 / 1.0000 |
| doubao21l | ce | syntax | rag2 vs rag | 84 | +1.59 [-2.78, +6.35] | 0.6291 | 1.0000 | 1.0000 | +0.80 / 1.0000 |
| doubao21l | he | direct | rag2 vs rag | 164 | -0.41 [-3.66, +2.85] | 0.9066 | 1.0000 | 1.0000 | -0.00 / 1.0000 |
| doubao21l | he | syntax | rag2 vs rag | 164 | -0.61 [-2.24, +1.22] | 0.6784 | 1.0000 | 1.0000 | -0.61 / 1.0000 |
| doubao21l | or | direct | rag2 vs rag | 30 | +3.33 [-2.22, +8.89] | 0.4524 | 1.0000 | 1.0000 | +3.33 / 1.0000 |
| doubao21l | or | syntax | rag2 vs rag | 30 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 | 1.0000 | +1.11 / 1.0000 |
| doubao_mini | ce | direct | rag2 vs rag | 84 | -1.59 [-7.54, +4.37] | 0.6947 | 1.0000 | 1.0000 | -1.61 / 1.0000 |
| doubao_mini | ce | syntax | rag2 vs rag | 84 | -2.78 [-6.35, +0.79] | 0.2055 | 1.0000 | 1.0000 | -2.81 / 1.0000 |
| doubao_mini | he | direct | rag2 vs rag | 164 | -1.02 [-5.69, +3.66] | 0.7375 | 1.0000 | 1.0000 | -0.82 / 1.0000 |
| doubao_mini | he | syntax | rag2 vs rag | 164 | +0.61 [-2.44, +3.66] | 0.7971 | 1.0000 | 1.0000 | +0.61 / 1.0000 |
| doubao_mini | or | direct | rag2 vs rag | 30 | +11.11 [+2.22, +21.11] | 0.0668 | 1.0000 | 1.0000 | +11.11 / 1.0000 |
| doubao_mini | or | syntax | rag2 vs rag | 30 | -4.44 [-14.44, +3.33] | 0.5180 | 1.0000 | 1.0000 | -4.44 / 1.0000 |
| ds_v41f | ce | direct | rag2 vs rag | 84 | -1.19 [-3.97, +1.98] | 0.6161 | 1.0000 | 1.0000 | -0.80 / 1.0000 |
| ds_v41f | ce | syntax | rag2 vs rag | 84 | +0.40 [-1.98, +2.78] | 1.0000 | 1.0000 | 1.0000 | +0.80 / 1.0000 |
| ds_v41f | he | direct | rag2 vs rag | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| ds_v41f | he | syntax | rag2 vs rag | 164 | -0.41 [-1.22, +0.00] | 1.0000 | 1.0000 | 1.0000 | -0.41 / 1.0000 |
| ds_v41f | or | direct | rag2 vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| ds_v41f | or | syntax | rag2 vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| glm53f | ce | direct | rag2 vs rag | 84 | +0.79 [-3.57, +5.56] | 0.8738 | 1.0000 | 1.0000 | -0.49 / 1.0000 |
| glm53f | he | direct | rag2 vs rag | 164 | +0.41 [-0.41, +1.63] | 0.7520 | 1.0000 | 1.0000 | +0.41 / 1.0000 |
| glm53f | he | syntax | rag2 vs rag | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| glm53f | or | direct | rag2 vs rag | 30 | -3.33 [-8.89, +0.00] | 0.5072 | 1.0000 | 1.0000 | -3.33 / 1.0000 |
| glm53f | or | syntax | rag2 vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| gpt6l | ce | direct | rag2 vs rag | 84 | -2.78 [-5.95, -0.00] | 0.1285 | 1.0000 | 1.0000 | -2.81 / 1.0000 |
| gpt6l | ce | syntax | rag2 vs rag | 84 | +0.40 [-2.38, +3.17] | 1.0000 | 1.0000 | 1.0000 | +0.40 / 1.0000 |
| gpt6l | he | direct | rag2 vs rag | 164 | -0.20 [-1.42, +1.02] | 1.0000 | 1.0000 | 1.0000 | -0.20 / 1.0000 |
| gpt6l | he | syntax | rag2 vs rag | 164 | -0.81 [-2.03, +0.00] | 0.2456 | 1.0000 | 1.0000 | -0.82 / 1.0000 |
| gpt6l | or | direct | rag2 vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| gpt6l | or | syntax | rag2 vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | ce | direct | rag2 vs rag | 84 | +1.19 [-1.98, +4.76] | 0.6821 | 1.0000 | 1.0000 | +0.80 / 1.0000 |
| haiku55 | ce | syntax | rag2 vs rag | 84 | -0.40 [-2.38, +1.19] | 1.0000 | 1.0000 | 1.0000 | -0.40 / 1.0000 |
| haiku55 | he | direct | rag2 vs rag | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | he | syntax | rag2 vs rag | 164 | +0.20 [+0.00, +0.61] | 1.0000 | 1.0000 | 1.0000 | +0.20 / 1.0000 |
| haiku55 | or | direct | rag2 vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| haiku55 | or | syntax | rag2 vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | ce | direct | rag2 vs rag | 84 | -2.38 [-6.35, +1.59] | 0.3632 | 1.0000 | 1.0000 | -2.41 / 1.0000 |
| kimik31p | ce | syntax | rag2 vs rag | 84 | -1.59 [-3.97, +0.79] | 0.3466 | 1.0000 | 1.0000 | -1.61 / 1.0000 |
| kimik31p | he | direct | rag2 vs rag | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | he | syntax | rag2 vs rag | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | or | direct | rag2 vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| kimik31p | or | syntax | rag2 vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| mm31f | ce | direct | rag2 vs rag | 84 | +3.17 [-0.79, +7.14] | 0.1875 | 1.0000 | 1.0000 | +3.21 / 1.0000 |
| mm31f | ce | syntax | rag2 vs rag | 84 | +0.40 [-3.17, +3.17] | 1.0000 | 1.0000 | 1.0000 | +0.40 / 1.0000 |
| mm31f | he | direct | rag2 vs rag | 164 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| mm31f | he | syntax | rag2 vs rag | 164 | +0.20 [+0.00, +0.61] | 1.0000 | 1.0000 | 1.0000 | +0.20 / 1.0000 |
| mm31f | or | direct | rag2 vs rag | 30 | -0.00 [-3.33, +3.33] | 1.0000 | 1.0000 | 1.0000 | -0.00 / 1.0000 |
| mm31f | or | syntax | rag2 vs rag | 30 | -1.11 [-3.33, +0.00] | 1.0000 | 1.0000 | 1.0000 | -1.11 / 1.0000 |
| u2f | ce | direct | rag2 vs rag | 84 | +0.79 [-2.78, +3.97] | 0.8251 | 1.0000 | 1.0000 | +0.80 / 1.0000 |
| u2f | ce | syntax | rag2 vs rag | 84 | -1.98 [-5.95, +2.38] | 0.4661 | 1.0000 | 1.0000 | -2.01 / 1.0000 |
| u2f | he | direct | rag2 vs rag | 164 | +0.61 [-0.41, +1.83] | 0.5337 | 1.0000 | 1.0000 | +0.61 / 1.0000 |
| u2f | he | syntax | rag2 vs rag | 164 | -0.81 [-1.83, +0.20] | 0.2201 | 1.0000 | 1.0000 | -0.82 / 1.0000 |
| u2f | or | direct | rag2 vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |
| u2f | or | syntax | rag2 vs rag | 30 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 | 1.0000 | +0.00 / 1.0000 |

## syntax × hint 交互效应

I = (hint − raw)<sub>direct</sub> − (hint − raw)<sub>syntax</sub>（百分点，按题计算）；I > 0 表示有语法手册时 hint 的增益更小。族 I 为验证性（族内 Holm）；I-explore 的数据已在第 3 阶段看过，只作探索性参考（单独 Holm）。

| 族 | 模型 | 数据集 | 题数 | hint 增益（direct） | hint 增益（syntax） | 交互 I [95% CI] | p | p(Holm) |
|---|---|---|---|---|---|---|---|---|
| I | doubao21l | ce | 84 | +13.49 | +0.40 | +13.10 [+6.75, +19.84] | 0.0005 | 0.0100 |
| I | doubao21l | he | 164 | +9.76 | +0.81 | +8.94 [+5.28, +13.01] | <0.0001 | 0.0021 |
| I | doubao21l | or | 30 | +16.67 | +0.00 | +16.67 [+5.56, +28.89] | 0.0151 | 0.2869 |
| I-explore | doubao_mini | ce | 84 | +1.98 | +1.19 | +0.79 [-3.17, +4.37] | 0.8384 | 1.0000 |
| I-explore | doubao_mini | he | 164 | +15.85 | +1.22 | +14.63 [+9.96, +19.31] | <0.0001 | 0.0006 |
| I-explore | doubao_mini | or | 30 | +16.67 | +7.78 | +8.89 [-3.33, +21.11] | 0.2191 | 1.0000 |
| I-explore | ds_v41f | ce | 84 | +1.19 | +2.38 | -1.19 [-5.56, +3.17] | 0.7393 | 1.0000 |
| I-explore | ds_v41f | he | 164 | +0.00 | +0.00 | +0.00 [-0.61, +0.61] | 1.0000 | 1.0000 |
| I-explore | ds_v41f | or | 30 | +1.11 | +0.00 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 |
| I | glm53f | ce | 84 | +2.78 | -0.79 | +3.57 [-2.38, +10.32] | 0.3245 | 1.0000 |
| I | glm53f | he | 164 | +0.41 | +0.00 | +0.41 [+0.00, +1.02] | 0.4988 | 1.0000 |
| I | glm53f | or | 30 | -1.11 | +0.00 | -1.11 [-3.33, +0.00] | 1.0000 | 1.0000 |
| I | gpt6l | ce | 84 | +0.00 | -0.00 | +0.00 [-2.78, +2.78] | 1.0000 | 1.0000 |
| I | gpt6l | he | 164 | +1.42 | -1.22 | +2.64 [+0.61, +5.28] | 0.0394 | 0.7091 |
| I | gpt6l | or | 30 | +2.22 | +0.00 | +2.22 [+0.00, +6.67] | 1.0000 | 1.0000 |
| I | haiku55 | ce | 84 | +0.79 | -0.40 | +1.19 [-3.97, +5.95] | 0.7646 | 1.0000 |
| I | haiku55 | he | 164 | +0.00 | +0.00 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 |
| I | haiku55 | or | 30 | +0.00 | +0.00 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 |
| I | kimik31p | ce | 84 | +1.19 | +1.59 | -0.40 [-3.17, +2.38] | 1.0000 | 1.0000 |
| I | kimik31p | he | 164 | +0.00 | +0.00 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 |
| I | kimik31p | or | 30 | +0.00 | +0.00 | +0.00 [+0.00, +0.00] | 1.0000 | 1.0000 |
| I | mm31f | ce | 84 | +0.00 | -0.40 | +0.40 [-3.97, +5.16] | 1.0000 | 1.0000 |
| I | mm31f | he | 164 | +1.22 | +0.61 | +0.61 [-0.81, +2.03] | 0.5891 | 1.0000 |
| I | mm31f | or | 30 | +1.11 | +0.00 | +1.11 [+0.00, +3.33] | 1.0000 | 1.0000 |
| I | u2f | ce | 84 | +0.00 | +2.78 | -2.78 [-9.52, +3.97] | 0.4975 | 1.0000 |
| I | u2f | he | 164 | -0.41 | -0.81 | +0.41 [-1.02, +2.03] | 0.7939 | 1.0000 |
| I | u2f | or | 30 | +0.00 | +1.11 | -1.11 [-5.56, +2.22] | 1.0000 | 1.0000 |

## Agent 行为（描述性）

| 模型 | 数据集 | 起点 | 组 | 题次 | 每题检索次数 | 至少检索一次 | 无效动作 | 平均步数 |
|---|---|---|---|---|---|---|---|---|
| doubao21l | ce | direct | agent | 252 | 0.992 | 62.7% | 1 | 4.25 |
| doubao21l | ce | direct | agent15 | 252 | 2.611 | 69.8% | 1 | 9.84 |
| doubao21l | ce | syntax | agent | 252 | 0.603 | 36.9% | 2 | 3.23 |
| doubao21l | ce | syntax | agent15 | 252 | 1.353 | 44.0% | 1 | 7.41 |
| doubao21l | he | direct | agent | 492 | 0.711 | 36.2% | 2 | 2.34 |
| doubao21l | he | direct | agent15 | 492 | 1.449 | 37.0% | 4 | 3.78 |
| doubao21l | he | syntax | agent | 492 | 0.126 | 7.7% | 4 | 0.54 |
| doubao21l | he | syntax | agent15 | 492 | 0.181 | 8.3% | 7 | 0.75 |
| doubao21l | or | direct | agent | 90 | 0.744 | 37.8% | 1 | 2.59 |
| doubao21l | or | direct | agent15 | 90 | 1.544 | 42.2% | 1 | 4.6 |
| doubao21l | or | syntax | agent | 90 | 0.2 | 11.1% | 0 | 0.57 |
| doubao21l | or | syntax | agent15 | 90 | 0.267 | 11.1% | 0 | 0.91 |
| doubao_mini | ce | direct | agent | 252 | 0.032 | 3.2% | 0 | 4.71 |
| doubao_mini | ce | direct | agent15 | 252 | 0.056 | 5.2% | 0 | 13.32 |
| doubao_mini | ce | syntax | agent | 252 | 0.119 | 8.3% | 0 | 4.16 |
| doubao_mini | ce | syntax | agent15 | 252 | 0.067 | 5.2% | 1 | 10.98 |
| doubao_mini | he | direct | agent | 492 | 0.03 | 2.8% | 4 | 3.85 |
| doubao_mini | he | direct | agent15 | 492 | 0.053 | 4.7% | 9 | 8.86 |
| doubao_mini | he | syntax | agent | 492 | 0.024 | 2.2% | 2 | 1.66 |
| doubao_mini | he | syntax | agent15 | 492 | 0.02 | 1.4% | 8 | 2.91 |
| doubao_mini | or | direct | agent | 90 | 0.056 | 5.6% | 0 | 4.29 |
| doubao_mini | or | direct | agent15 | 90 | 0.1 | 8.9% | 0 | 9.73 |
| doubao_mini | or | syntax | agent | 90 | 0.022 | 2.2% | 0 | 1.63 |
| doubao_mini | or | syntax | agent15 | 90 | 0.022 | 2.2% | 1 | 2.97 |
| ds_v41f | ce | direct | agent | 252 | 0.762 | 44.0% | 3 | 2.57 |
| ds_v41f | ce | direct | agent15 | 252 | 1.726 | 51.6% | 19 | 5.37 |
| ds_v41f | ce | syntax | agent | 252 | 0.536 | 28.6% | 2 | 2.31 |
| ds_v41f | ce | syntax | agent15 | 252 | 1.278 | 32.1% | 16 | 5.21 |
| ds_v41f | he | direct | agent | 492 | 0.193 | 13.2% | 0 | 0.48 |
| ds_v41f | he | direct | agent15 | 492 | 0.213 | 12.4% | 0 | 0.52 |
| ds_v41f | he | syntax | agent | 492 | 0.053 | 5.1% | 0 | 0.18 |
| ds_v41f | he | syntax | agent15 | 492 | 0.079 | 6.1% | 0 | 0.23 |
| ds_v41f | or | direct | agent | 90 | 0.233 | 14.4% | 0 | 0.74 |
| ds_v41f | or | direct | agent15 | 90 | 0.278 | 17.8% | 0 | 0.79 |
| ds_v41f | or | syntax | agent | 90 | 0.0 | 0.0% | 0 | 0.1 |
| ds_v41f | or | syntax | agent15 | 90 | 0.044 | 2.2% | 0 | 0.14 |
| glm53f | ce | direct | agent | 252 | 0.639 | 29.4% | 50 | 2.64 |
| glm53f | ce | direct | agent15 | 252 | 1.444 | 34.1% | 205 | 5.12 |
| glm53f | ce | syntax | agent | 252 | 0.349 | 14.3% | 59 | 2.04 |
| glm53f | ce | syntax | agent15 | 252 | 0.687 | 21.0% | 179 | 3.79 |
| glm53f | he | direct | agent | 492 | 0.104 | 6.5% | 3 | 0.57 |
| glm53f | he | direct | agent15 | 492 | 0.136 | 7.9% | 2 | 0.59 |
| glm53f | he | syntax | agent | 492 | 0.01 | 1.0% | 2 | 0.1 |
| glm53f | he | syntax | agent15 | 492 | 0.03 | 1.8% | 0 | 0.12 |
| glm53f | or | direct | agent | 90 | 0.167 | 8.9% | 2 | 1.14 |
| glm53f | or | direct | agent15 | 90 | 0.167 | 10.0% | 6 | 1.23 |
| glm53f | or | syntax | agent | 90 | 0.0 | 0.0% | 0 | 0.13 |
| glm53f | or | syntax | agent15 | 90 | 0.0 | 0.0% | 0 | 0.13 |
| gpt6l | ce | direct | agent | 252 | 0.262 | 14.7% | 0 | 2.67 |
| gpt6l | ce | direct | agent15 | 252 | 0.46 | 17.1% | 0 | 5.84 |
| gpt6l | ce | syntax | agent | 252 | 0.198 | 9.1% | 0 | 2.67 |
| gpt6l | ce | syntax | agent15 | 252 | 0.361 | 11.9% | 0 | 6.16 |
| gpt6l | he | direct | agent | 492 | 0.185 | 9.3% | 0 | 0.8 |
| gpt6l | he | direct | agent15 | 492 | 0.388 | 11.2% | 0 | 1.23 |
| gpt6l | he | syntax | agent | 492 | 0.049 | 2.4% | 0 | 0.24 |
| gpt6l | he | syntax | agent15 | 492 | 0.063 | 2.8% | 0 | 0.37 |
| gpt6l | or | direct | agent | 90 | 0.244 | 11.1% | 0 | 0.81 |
| gpt6l | or | direct | agent15 | 90 | 0.467 | 12.2% | 0 | 1.04 |
| gpt6l | or | syntax | agent | 90 | 0.0 | 0.0% | 0 | 0.07 |
| gpt6l | or | syntax | agent15 | 90 | 0.0 | 0.0% | 0 | 0.07 |
| haiku55 | ce | direct | agent | 252 | 0.23 | 21.4% | 12 | 2.55 |
| haiku55 | ce | direct | agent15 | 252 | 1.071 | 39.7% | 142 | 5.85 |
| haiku55 | ce | syntax | agent | 252 | 0.468 | 33.3% | 14 | 2.28 |
| haiku55 | ce | syntax | agent15 | 252 | 1.552 | 39.7% | 152 | 5.65 |
| haiku55 | he | direct | agent | 492 | 0.022 | 2.2% | 0 | 0.34 |
| haiku55 | he | direct | agent15 | 492 | 0.008 | 0.8% | 0 | 0.31 |
| haiku55 | he | syntax | agent | 492 | 0.016 | 1.4% | 0 | 0.1 |
| haiku55 | he | syntax | agent15 | 492 | 0.016 | 1.6% | 0 | 0.1 |
| haiku55 | or | direct | agent | 90 | 0.011 | 1.1% | 0 | 0.37 |
| haiku55 | or | direct | agent15 | 90 | 0.0 | 0.0% | 0 | 0.36 |
| haiku55 | or | syntax | agent | 90 | 0.0 | 0.0% | 0 | 0.1 |
| haiku55 | or | syntax | agent15 | 90 | 0.0 | 0.0% | 0 | 0.1 |
| kimik31p | ce | direct | agent | 252 | 0.639 | 29.0% | 0 | 2.15 |
| kimik31p | ce | direct | agent15 | 252 | 1.063 | 29.4% | 0 | 3.77 |
| kimik31p | ce | syntax | agent | 252 | 0.425 | 18.7% | 0 | 1.91 |
| kimik31p | ce | syntax | agent15 | 252 | 0.778 | 20.6% | 1 | 3.23 |
| kimik31p | he | direct | agent | 492 | 0.234 | 11.2% | 0 | 0.49 |
| kimik31p | he | direct | agent15 | 492 | 0.26 | 11.8% | 0 | 0.52 |
| kimik31p | he | syntax | agent | 492 | 0.055 | 3.7% | 0 | 0.14 |
| kimik31p | he | syntax | agent15 | 492 | 0.026 | 2.2% | 0 | 0.11 |
| kimik31p | or | direct | agent | 90 | 0.256 | 13.3% | 0 | 0.67 |
| kimik31p | or | direct | agent15 | 90 | 0.211 | 10.0% | 0 | 0.58 |
| kimik31p | or | syntax | agent | 90 | 0.044 | 1.1% | 0 | 0.08 |
| kimik31p | or | syntax | agent15 | 90 | 0.044 | 2.2% | 0 | 0.11 |
| mm31f | ce | direct | agent | 252 | 1.762 | 57.9% | 1 | 3 |
| mm31f | ce | direct | agent15 | 252 | 5.698 | 57.5% | 1 | 7.63 |
| mm31f | ce | syntax | agent | 252 | 1.357 | 48.0% | 0 | 2.51 |
| mm31f | ce | syntax | agent15 | 252 | 4.873 | 48.8% | 1 | 6.49 |
| mm31f | he | direct | agent | 492 | 0.356 | 14.2% | 0 | 0.74 |
| mm31f | he | direct | agent15 | 492 | 0.671 | 15.0% | 0 | 1.11 |
| mm31f | he | syntax | agent | 492 | 0.136 | 7.5% | 0 | 0.33 |
| mm31f | he | syntax | agent15 | 492 | 0.22 | 7.9% | 0 | 0.42 |
| mm31f | or | direct | agent | 90 | 0.511 | 17.8% | 0 | 1.04 |
| mm31f | or | direct | agent15 | 90 | 1.322 | 18.9% | 0 | 1.94 |
| mm31f | or | syntax | agent | 90 | 0.144 | 6.7% | 0 | 0.37 |
| mm31f | or | syntax | agent15 | 90 | 0.511 | 8.9% | 0 | 0.78 |
| u2f | ce | direct | agent | 252 | 0.433 | 27.8% | 81 | 2.96 |
| u2f | ce | direct | agent15 | 252 | 1.183 | 42.5% | 132 | 5.77 |
| u2f | ce | syntax | agent | 252 | 0.361 | 18.7% | 84 | 2.57 |
| u2f | ce | syntax | agent15 | 252 | 0.972 | 31.3% | 166 | 5.42 |
| u2f | he | direct | agent | 492 | 0.161 | 11.2% | 74 | 1.05 |
| u2f | he | direct | agent15 | 492 | 0.207 | 12.0% | 90 | 1.22 |
| u2f | he | syntax | agent | 492 | 0.079 | 6.3% | 76 | 0.73 |
| u2f | he | syntax | agent15 | 492 | 0.12 | 7.5% | 73 | 0.75 |
| u2f | or | direct | agent | 90 | 0.122 | 7.8% | 11 | 1.07 |
| u2f | or | direct | agent15 | 90 | 0.222 | 12.2% | 6 | 1.1 |
| u2f | or | syntax | agent | 90 | 0.056 | 4.4% | 7 | 0.38 |
| u2f | or | syntax | agent15 | 90 | 0.011 | 1.1% | 4 | 0.28 |
