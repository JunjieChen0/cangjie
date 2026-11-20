# 第 0 轮编译错误分类器：人工盲评复核

共 60 条（按分类器类别分层抽样，每类最多 15 条，评分时看不到分类器结果）。

样本内完全一致 44/60（73.3%），Cohen κ = 0.644。
按各类别在全部 609 条第 0 轮编译错误中的占比加权，估计分类器总体准确率为 **92.2%**（分层抽样的标准估计）。

| 类别 | 总体条数 | 分类器判为（样本） | 人工判为（样本） | 精确率 | 召回率（样本内） |
|---|---:|---:|---:|---:|---:|
| foreign_syntax | 297 | 15 | 23 | 1.0 | 0.652 |
| api_or_undeclared | 215 | 15 | 16 | 0.867 | 0.812 |
| type_or_mutability | 77 | 15 | 20 | 1.0 | 0.75 |
| duplicate_main | 0 | 0 | 0 | — | — |
| other_compile | 20 | 15 | 1 | 0.067 | 1.0 |

不一致（分类器 → 人工：条数）：api_or_undeclared → type_or_mutability：2；other_compile → api_or_undeclared：3；other_compile → foreign_syntax：8；other_compile → type_or_mutability：3

注：分层抽样使各类别等量出现，精确率可直接解读；召回率与总体一致率受抽样比例影响，只作参考。
