# 检索方案离线评估（自动生成）

数据：第 2 阶段修复反馈，按报错类别各抽 30 条（种子 7）；判定模型 deepseek-v4-pro-ga-260813；改写模型 doubao-seed-2-0-mini-260428。
hit@3 = top-3 中至少一个片段含修复所需写法（2 分）；any@3 = 至少一个相关（≥1 分）；nDCG@3 以该题全部被判定片段为理想排序。数值为百分比。

## all（150 条）

| 检索器 | hit@3 | any@3 | nDCG@3 |
|---|---|---|---|
| bm25 | 46.7 | 78.7 | 46.9 |
| rewrite_bm25 | 40.0 | 72.0 | 47.1 |
| dense | 28.0 | 76.0 | 46.8 |
| hybrid | 38.0 | 84.7 | 54.0 |
| hybrid_rerank | 35.3 | 82.7 | 46.7 |
| rewrite_hybrid_rerank | 52.7 | 88.7 | 64.0 |

## foreign_syntax（30 条）

| 检索器 | hit@3 | any@3 | nDCG@3 |
|---|---|---|---|
| bm25 | 66.7 | 86.7 | 51.7 |
| rewrite_bm25 | 36.7 | 56.7 | 26.0 |
| dense | 26.7 | 53.3 | 23.6 |
| hybrid | 50.0 | 73.3 | 40.9 |
| hybrid_rerank | 50.0 | 76.7 | 41.3 |
| rewrite_hybrid_rerank | 70.0 | 80.0 | 63.5 |

## api_or_undeclared（30 条）

| 检索器 | hit@3 | any@3 | nDCG@3 |
|---|---|---|---|
| bm25 | 46.7 | 80.0 | 47.8 |
| rewrite_bm25 | 56.7 | 86.7 | 62.1 |
| dense | 53.3 | 96.7 | 59.6 |
| hybrid | 50.0 | 86.7 | 62.0 |
| hybrid_rerank | 46.7 | 86.7 | 54.8 |
| rewrite_hybrid_rerank | 56.7 | 90.0 | 67.1 |

## type_or_mutability（30 条）

| 检索器 | hit@3 | any@3 | nDCG@3 |
|---|---|---|---|
| bm25 | 30.0 | 56.7 | 28.9 |
| rewrite_bm25 | 30.0 | 70.0 | 34.3 |
| dense | 26.7 | 60.0 | 39.9 |
| hybrid | 40.0 | 80.0 | 40.1 |
| hybrid_rerank | 26.7 | 66.7 | 26.7 |
| rewrite_hybrid_rerank | 46.7 | 96.7 | 56.5 |

## other_compile（30 条）

| 检索器 | hit@3 | any@3 | nDCG@3 |
|---|---|---|---|
| bm25 | 53.3 | 73.3 | 40.8 |
| rewrite_bm25 | 36.7 | 53.3 | 39.4 |
| dense | 30.0 | 70.0 | 37.7 |
| hybrid | 50.0 | 83.3 | 52.8 |
| hybrid_rerank | 50.0 | 83.3 | 47.8 |
| rewrite_hybrid_rerank | 46.7 | 80.0 | 53.5 |

## runtime_exception（30 条）

| 检索器 | hit@3 | any@3 | nDCG@3 |
|---|---|---|---|
| bm25 | 36.7 | 96.7 | 65.1 |
| rewrite_bm25 | 40.0 | 93.3 | 73.5 |
| dense | 3.3 | 100.0 | 73.0 |
| hybrid | 0.0 | 100.0 | 74.2 |
| hybrid_rerank | 3.3 | 100.0 | 62.7 |
| rewrite_hybrid_rerank | 43.3 | 96.7 | 79.3 |
