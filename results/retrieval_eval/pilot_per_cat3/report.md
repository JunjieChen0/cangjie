# 检索方案离线评估（自动生成）

数据：第 2 阶段修复反馈，按报错类别各抽 3 条（种子 7）；判定模型 deepseek-v4-pro-ga-260813；改写模型 doubao-seed-2-0-mini-260428。
hit@3 = top-3 中至少一个片段含修复所需写法（2 分）；any@3 = 至少一个相关（≥1 分）；nDCG@3 以该题全部被判定片段为理想排序。数值为百分比。

## all（15 条）

| 检索器 | hit@3 | any@3 | nDCG@3 |
|---|---|---|---|
| bm25 | 73.3 | 100.0 | 64.8 |
| rewrite_bm25 | 26.7 | 60.0 | 42.6 |
| dense | 20.0 | 73.3 | 43.5 |
| hybrid | 53.3 | 86.7 | 56.2 |
| hybrid_rerank | 26.7 | 86.7 | 47.9 |
| rewrite_hybrid_rerank | 46.7 | 80.0 | 63.2 |

## foreign_syntax（3 条）

| 检索器 | hit@3 | any@3 | nDCG@3 |
|---|---|---|---|
| bm25 | 66.7 | 100.0 | 63.4 |
| rewrite_bm25 | 33.3 | 33.3 | 14.5 |
| dense | 0.0 | 66.7 | 16.7 |
| hybrid | 66.7 | 100.0 | 32.3 |
| hybrid_rerank | 0.0 | 66.7 | 23.8 |
| rewrite_hybrid_rerank | 66.7 | 66.7 | 57.7 |

## api_or_undeclared（3 条）

| 检索器 | hit@3 | any@3 | nDCG@3 |
|---|---|---|---|
| bm25 | 100.0 | 100.0 | 85.2 |
| rewrite_bm25 | 66.7 | 100.0 | 75.5 |
| dense | 66.7 | 100.0 | 70.6 |
| hybrid | 100.0 | 100.0 | 87.2 |
| hybrid_rerank | 66.7 | 100.0 | 50.0 |
| rewrite_hybrid_rerank | 66.7 | 100.0 | 71.6 |

## type_or_mutability（3 条）

| 检索器 | hit@3 | any@3 | nDCG@3 |
|---|---|---|---|
| bm25 | 66.7 | 100.0 | 44.0 |
| rewrite_bm25 | 0.0 | 0.0 | 0.0 |
| dense | 0.0 | 33.3 | 8.8 |
| hybrid | 33.3 | 66.7 | 49.0 |
| hybrid_rerank | 0.0 | 66.7 | 13.8 |
| rewrite_hybrid_rerank | 33.3 | 100.0 | 59.2 |

## other_compile（3 条）

| 检索器 | hit@3 | any@3 | nDCG@3 |
|---|---|---|---|
| bm25 | 100.0 | 100.0 | 76.5 |
| rewrite_bm25 | 33.3 | 66.7 | 39.5 |
| dense | 33.3 | 66.7 | 46.0 |
| hybrid | 33.3 | 66.7 | 35.1 |
| hybrid_rerank | 66.7 | 100.0 | 68.5 |
| rewrite_hybrid_rerank | 33.3 | 33.3 | 27.7 |

## runtime_exception（3 条）

| 检索器 | hit@3 | any@3 | nDCG@3 |
|---|---|---|---|
| bm25 | 33.3 | 100.0 | 54.7 |
| rewrite_bm25 | 0.0 | 100.0 | 83.3 |
| dense | 0.0 | 100.0 | 75.5 |
| hybrid | 33.3 | 100.0 | 77.4 |
| hybrid_rerank | 0.0 | 100.0 | 83.3 |
| rewrite_hybrid_rerank | 33.3 | 100.0 | 100.0 |
