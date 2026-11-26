# 敏感性分析汇总：判定不稳定的题与超时题（自动生成）

去掉的题：ce 第 58 题；he 第 20 题（参考答案重复运行时判定不稳定，原因见 stage3_stats.py 中 FLAKY 的注释）；并且每个比较中，两组任一次重复里 API 超时的题从两组同时去掉（超时只出现在 glm53f、kimik31p，主分析中按未通过计入分母，不过滤）。

「结论改变」= Holm 校正后的显著性（α = 0.05）改变，或差值正负号改变。

## 第 3 阶段（33 个预先设定的比较）

比较 33 个；Holm 显著：全部题 9 个 → 去掉后 9 个；差值最大变化 0.75 个百分点。

没有比较的结论发生改变。

超时（按未通过计入主分析）：kimik31p ce direct hint：7 题次（1 次重复合计）；kimik31p ce direct raw：11 题次（1 次重复合计）；kimik31p he direct hint：1 题次（3 次重复合计）；kimik31p he direct raw：4 题次（3 次重复合计）。

## Original-30（17 个预先设定的比较）

比较 17 个；Holm 显著：全部题 2 个 → 去掉后 2 个；差值最大变化 1.11 个百分点。

没有比较的结论发生改变。

超时（按未通过计入主分析）：kimik31p or direct hint：1 题次（3 次重复合计）。

## 补充实验（族 G / A / R，各族内 Holm）

比较 346 个；Holm 显著：全部题 40 个 → 去掉后 40 个；差值最大变化 3.55 个百分点。

| 族 | 模型 | 数据集 | 起点 | A vs B | 差值 / p(Holm)（全部题） | 题数（去掉后） | 差值 / p(Holm)（去掉后） |
|---|---|---|---|---|---|---|---|
| G | glm53f | ce | direct | rag vs hint | -1.59 / 1.0000 | 68 | +1.96 / 1.0000 |
| A | ds_v41f | ce | direct | agent15 vs agent | +8.73 / 0.0376 | 83 | +8.43 / 0.0728 |
| A | glm53f | ce | syntax | agent vs rag | +0.79 / 1.0000 | 79 | -1.27 / 1.0000 |
| A | u2f | ce | syntax | agent15 vs agent | +8.33 / 0.0546 | 83 | +8.84 / 0.0460 |
| R | glm53f | ce | direct | rag2 vs rag | +0.79 / 1.0000 | 68 | -0.49 / 1.0000 |

超时（按未通过计入主分析）：glm53f ce direct agent：2 题次（3 次重复合计）；glm53f ce direct agent15：1 题次（3 次重复合计）；glm53f ce direct hint：3 题次（3 次重复合计）；glm53f ce direct rag：21 题次（3 次重复合计）；glm53f ce direct rag2：1 题次（3 次重复合计）；glm53f ce syntax agent：1 题次（3 次重复合计）；glm53f ce syntax agent15：13 题次（3 次重复合计）；glm53f ce syntax blind：1 题次（3 次重复合计）；glm53f ce syntax hint：1 题次（3 次重复合计）；glm53f ce syntax rag：4 题次（3 次重复合计）；glm53f ce syntax raw：3 题次（3 次重复合计）；glm53f he direct hint：1 题次（3 次重复合计）。
