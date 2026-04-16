# Thesis Brainstorm 3.0

## 0. One-Sentence Summary

当前毕业论文最稳的主线应当是：

> 以 relation pattern 为切入点，分析 KGE predictive multiplicity 的结构性差异；在此基础上，将 small committee / reduced voting 作为一个附加扩展，而不是主贡献。

---

## 1. Background

当前讨论的出发点来自 Zhu et al. 关于 KGE link prediction 中 predictive multiplicity 的工作。该论文已经完成了三件重要事情：

1. 定义并量化了 predictive multiplicity；
2. 证明了不同 seed 的近似等性能模型会对同一 query 给出冲突预测；
3. 说明 voting methods 可以缓解这一问题。

但这篇论文对于“为什么某些 relation 更容易出现 multiplicity”并没有做系统化研究。它真正做过的相关分析主要包括：

- error tolerance \(\epsilon\) 与 multiplicity 的关系；
- aggregation 使用模型数目的影响；
- entity/relation frequency 与 multiplicity 的关系；
- 对 expressiveness、inverse pattern、symmetric relation 等因素的初步讨论。

因此，一个自然且更适合毕业论文的后续问题是：

> multiplicity 是否不是均匀发生的，而是与 relation 的结构模式有关？

---

## 2. Why 3.0 Is Different

与 1.0 相比，3.0 不再把“模型选择器 / selector / router”作为默认主线。  
与 2.0 相比，3.0 又进一步把“small committee”从潜在主线降级为辅助扩展。

原因如下：

### 2.1 为什么不把 selector 当主线

selector 的难点不在于不能做，而在于它会把论文推向更大的工程问题：

- 需要先证明不同模型在不同 relation 上确实存在稳定互补性；
- 需要设计一个可解释的 selector；
- 需要证明 selector 的增益是稳定而不是偶然；
- 答辩时很容易被问“为什么不直接 ensemble”。

这条路风险较高，不适合当前“顺利毕业优先”的目标。

### 2.2 为什么不把 small committee 当主线

前面已经讨论清楚：  
如果最终拿来计算 \(\alpha\) 和 \(\delta\) 的模型集合变小，那么 \(\alpha\) 和 \(\delta\) 本身就可能天然变小，因此不能直接把“更小的集合得到更小的 \(\alpha,\delta\)”当作主张。

所以，small committee 不能写成：

> 我的方法更好，因为 \(\alpha,\delta\) 更低。

更合理的写法应当是：

> 在已有模型池的前提下，是否可以用更小规模的 committee，近似 full voting 的效果，并以更低预算保留相近的 accuracy / mitigation trend。

这使得它更适合作为附加扩展，而不是主论文问题。

---

## 3. Core Thesis Question

当前最适合作为毕业论文主问题的是：

> 不同 relation pattern 下，KGE 的 predictive multiplicity 是否存在系统性差异？

这个问题可以再拆成三层：

1. **单模型内部层面**  
   对于固定 KGE 模型，不同 relation pattern 下的 multiplicity severity 是否不同？

2. **跨模型层面**  
   不同模型面对同一种 relation pattern 时，multiplicity profile 是否不同？

3. **扩展层面**  
   如果某些 relation pattern 下 multiplicity 更高，那么在已有模型池的前提下，small committee 是否仍能逼近 full voting？

---

## 4. Research Story

当前最稳的论文叙事不是：

- “我发明了一个更好的 voting 方法”
- “我设计了一个聪明的模型选择器”

而应该是：

1. KGE 中确实存在 predictive multiplicity；
2. multiplicity 不是均匀分布的，而是和 relation structure 有关；
3. 不同模型对不同 pattern 的稳定性敏感程度不同；
4. 在此基础上，full voting 可能存在冗余，因此 small committee 值得作为附加分析。

换句话说：

- **主线是分析与解释**
- **副线是效率与实用性**

---

## 5. Main Scope

### 5.1 Analysis Level

- 主分析粒度：**relation-level**
- 当前不做：**query-level selector / router**

### 5.2 Main Dataset

第一阶段只做：

- `FB15k-237`

第二阶段如果顺利，再补：

- `WN18RR`

### 5.3 Main Models

第一阶段建议只做：

- `RotatE`

第二阶段补：

- `TransE`

第三阶段若时间允许，再补：

- `ComplEx`

这里的逻辑是：

- **一个模型**足以回答：  
  “在这个模型里，不同 relation pattern 是否对应不同 multiplicity？”
- **两个模型**才能回答：  
  “这种 pattern effect 是通用现象，还是模型特有现象？”
- **第三个模型**主要用于增强可信度，而不是改变主线。

因此，对当前毕业目标来说：

- **最小可毕业版本**：RotatE + TransE
- **增强版本**：再补 ComplEx

---

## 6. Main Relation Patterns

当前建议只保留 4 个核心维度。

### 6.1 Mapping Type

离散分类：

- 1-1
- 1-N
- N-1
- N-N

这是最经典、最稳、最容易解释的维度。

### 6.2 Answer Cardinality

连续统计：

- average tail per \((h,r)\)
- average head per \((r,t)\)

它和 mapping type 不是独立宇宙，而是 mapping behavior 的连续化表达。  
因此在论文里更好的写法是：

- mapping type = 离散版
- answer cardinality = 连续版

### 6.3 Symmetry / Antisymmetry

建议不要一开始做成纯二元标签，而是先计算 relation-level symmetry score，再按阈值分桶。

理由：

- 真实 KG relation 往往不“纯”
- 连续 score 更稳

### 6.4 Inverse Relation Strength

对 relation pair 的 inverse evidence 做统计，为每个 relation 定义 inverse strength。

---

## 7. Patterns Not Recommended for Stage 1

当前不建议优先做：

- commutative / non-commutative
- hierarchy
- composition / additivity
- path-based composition
- query difficulty
- local structural support

理由不是它们没价值，而是：

- 定义更复杂
- 标注和计算更麻烦
- 容易把主线做散
- 对当前毕业目标不划算

这些可以保留在 brainstorm 里，但不要进入第一版主实验。

---

## 8. Main Metrics

当前最重要的不是堆太多 pattern，而是把 multiplicity 的量化方式定稳。

建议至少定义两类 relation-level 指标。

### 8.1 Relation-Level Multiplicity Severity

刻画同一个 relation 下，不同 repeated runs 的预测冲突有多严重。

可选实现包括：

- relation 内 baseline 与 competing runs 的 top-k 一致率
- relation 内 \(\alpha_r\)
- relation 内 \(\delta_r\)
- relation 内 Hits@10 波动

### 8.2 Relation-Level Voting Gain

刻画 voting 对某个 relation 是否真的有帮助。

可选实现包括：

- full voting vs best single run 的 Hits@10 提升
- full voting vs average single run 的提升

原则是：

- 先用简单、稳定、可解释的定义
- 不要一开始自造复杂指标

---

## 9. How to Understand “Why More Models?”

这个问题之前已经讨论得比较清楚，这里直接整理成最终版本。

### 9.1 如果只用一个模型

你可以回答：

> 在 RotatE 中，不同 relation pattern 是否对应不同 multiplicity？

这是成立的，也足够做出一个窄而完整的分析。

### 9.2 为什么还要补 TransE

因为补第二个模型后，你能多回答一个更重要的问题：

> 这种 pattern effect 是 relation structure 本身导致的，还是某个模型特有的？

也就是说：

- 如果 RotatE 和 TransE 都表现出相似趋势，那更像是 **pattern 本身在起作用**
- 如果只有 TransE 在某些 pattern 上特别不稳定，那更像是 **model-pattern interaction**

### 9.3 为什么 ComplEx 只是增强项

ComplEx 的作用不是必须性，而是提高结论可信度：

- 避免结论只停留在 “RotatE vs TransE”
- 说明现象不是两模型巧合

但如果时间不够，它完全可以不做。

---

## 10. About Small Committee / Reduced Voting

这一部分必须重新定义立足点。

### 10.1 它不应该怎么写

不能写成：

> 用更小模型集合得到了更小的 \(\alpha,\delta\)，所以方法更强。

因为最终评估集合变小，本来就可能让 \(\alpha,\delta\) 天然下降。

### 10.2 它应该怎么写

更稳的写法是：

> 在已有 \(\epsilon\)-valid model pool 的前提下，研究小规模随机子集 committee 是否可以在更低预算下逼近 full voting 的效果。

### 10.3 它在 3.0 中的角色

- 不是主线
- 不是论文第一章要解决的问题
- 是一个**附加扩展 / appendix-style study**

### 10.4 如果未来要做，最低要求

如果要把它写进去，至少要满足：

- 固定最终输出 aggregated model 数量
- 多个 grouping seed 重复
- 报 mean ± std
- 比较的是 “接近 full voting”，不是 “绝对更小的 \(\alpha,\delta\)”

---

## 11. Minimal Viable Thesis

如果目标只是“稳稳毕业”，那么最小可毕业版本可以定义为：

- 数据集：`FB15k-237`
- 模型：`RotatE + TransE`
- repeated runs：每个模型至少 8 个
- relation patterns：4 个
- multiplicity metrics：2 个
- 输出：relation-level 统计表、箱线图/条形图、模型间对比图

只要最后能说明：

1. 某些 relation pattern 下 multiplicity 明显更严重；
2. 这种现象在至少两个模型中都可观察；
3. 两个模型的 multiplicity profile 又不完全相同；

那么主线就已经成立。

---

## 12. Practical Execution Strategy

### Stage 0: Keep the Problem Small

不要再扩问题。  
当前最重要的不是“想更多 pattern”，而是“先把最小主线做扎实”。

### Stage 1: Run the Main Pipeline

先确保：

- repeated runs 能稳定读取
- multiplicity 主实验脚本能稳定输出
- relation-level 结果能聚合出来

### Stage 2: Build Relation Statistics Table

只做一次，共享给所有模型：

- mapping type
- answer cardinality
- symmetry score
- inverse strength
- optional: relation frequency

### Stage 3: RotatE First

先只做：

- `RotatE + FB15k-237`

目标不是交稿，而是验证：

- pattern 脚本没问题
- multiplicity 指标有区分度
- relation-level 统计能产出图和表

### Stage 4: Add TransE

补上：

- `TransE + FB15k-237`

目标是从“单模型现象”升级到“跨模型比较”。

### Stage 5: Optional ComplEx

如果前四步顺利，再补：

- `ComplEx`

### Stage 6: Optional Small Committee

只有主线已经稳定时，再做：

- fixed pool
- fixed final output size
- small committee vs full voting

---

## 13. Risk Control

当前最需要防止的，不是“想法不够新”，而是“问题做散”。

因此 3.0 的控制原则是：

1. 优先保住主线，不追求花哨扩展；
2. 优先做 relation-level，不做 query-level；
3. 优先做分析型结论，不急着做方法型系统；
4. 优先 RotatE，再 TransE；
5. 优先 4 个 pattern，不碰更多复杂属性；
6. small committee 永远放在副线。

如果中期发现 relation pattern 与 multiplicity 的关系没有想象中稳定，那么后备路线可以是：

> 不同 KGE 模型 predictive multiplicity 的经验分析，relation pattern 作为辅助解释变量。

这仍然是一条可毕业路线。

---

## 14. Final Positioning

当前最合适的论文定位不是：

- 我提出了一个新模型
- 我解决了 multiplicity
- 我发明了一个 selector

而是：

> 我系统分析了 relation pattern 与 predictive multiplicity 的关系，并观察到不同模型在不同 pattern 上的稳定性分布存在差异；在此基础上，我进一步考察了 small committee 是否能够近似 full voting。

---

## 15. Meeting Summary Version

如果想要一个更短、更像会议纪要的版本，可以记成下面这样：

### 这轮讨论的最终共识

1. 毕业论文主线确定为：**relation pattern 与 predictive multiplicity 的关系**。  
2. small committee / reduced voting 只作为**扩展分析**，不作为主贡献。  
3. relation-level 足够，不做 query-level。  
4. pattern 只保留四个：
   - mapping type
   - answer cardinality
   - symmetry / antisymmetry
   - inverse strength
5. 第一阶段只做 `RotatE + FB15k-237`。  
6. 第二阶段补 `TransE`，用于判断 pattern effect 是否模型相关。  
7. `ComplEx` 是增强项，不是必须项。  
8. 不碰 commutative / hierarchy / composition 这些更复杂的 pattern。  
9. small committee 不能再用“更小集合得到更小 alpha/delta”来讲故事。  
10. 当前最重要的是把主实验和 relation-level 统计跑通。

---

## 16. To-Do List

### A. 立刻做

1. 把 3.0 定为当前唯一主文档。
2. 明确主问题：relation pattern vs predictive multiplicity。
3. 明确副问题：small committee 只是扩展。
4. 明确第一阶段只做 `RotatE + FB15k-237`。

### B. 先跑通实验链路

1. 整理 RotatE repeated runs。
2. 确认 multiplicity evaluation 脚本能稳定输出。
3. 确认 relation-level 聚合结果能导出。

### C. 写 relation statistics 脚本

1. mapping type
2. answer cardinality
3. symmetry score
4. inverse strength
5. optional: relation frequency

### D. 先做第一版分析

1. 只分析 RotatE
2. 输出 relation-level 表格
3. 画不同 pattern 下 multiplicity severity 的图
4. 看有没有明显趋势

### E. 第二版增强

1. 加入 TransE
2. 做同样的 relation-level 分析
3. 对比两模型的 multiplicity profile

### F. 如果顺利再做

1. 补 ComplEx
2. 做 small committee vs full voting
3. 固定最终输出数，重复多 seed，报 mean ± std

### G. 暂时不要做

1. query-level selector
2. dynamic committee size
3. composition / additivity
4. hierarchy
5. commutative / non-commutative
6. 一上来就多数据集多模型全开
