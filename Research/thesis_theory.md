# 论文理论部分

## 本说明的范围

本说明用于明确论文主要分析主线的形式化定义：

> KGE 链接预测中的关系模式与预测多重性（predictive multiplicity）。

当前阶段的研究重点为：

* 数据集：`FB15k-237`
* 模型设定：对同一KGE模型进行多次重复训练
* 分析层级：`relation-level（关系层级）`
* 当前已推进模式：`mapping type（映射类型）`
* 下一步模式：`inverse strength（逆关系支持强度）`

本说明旨在在代码修改之前，确保实验术语的稳定性。

## 核心研究问题

核心问题为：

> 不同的关系映射类型，是否表现出系统性不同的预测多重性行为？

当前目标不是构建选择器或新的投票方法，而是对多重性模式进行分析与解释。

## 关系映射类型（Relation Mapping Type）

我们采用 LibKGE 中使用的标准关系类型划分方法，其来源可追溯至 Bordes 等人的工作：

* `1-1`
* `1-N`
* `M-1`
* `M-N`

在论文写作中，为了可读性，可以将 `M-1` 和 `M-N` 写作 `N-1` 和 `N-N`。但在代码和中间输出中，应保持 LibKGE 的命名方式，以避免混淆。

### 操作性定义

对于每个关系 `r`，LibKGE 基于训练数据中的平均连接性统计对其进行分类：

* 若 `(h, r)` 对应的平均尾实体数量大于 `1.5`，则认为尾侧为多（many）
* 若 `(r, t)` 对应的平均头实体数量大于 `1.5`，则认为头侧为多（many）

由此得到上述四种映射类型。

因此，在当前论文设定中，`N` 并不是符号意义上的“多”，而是由 LibKGE 使用阈值 `1.5` 的操作性定义所决定。

## 关系层级分析单元

核心分析单元是关系 `r`，而不是单个查询，也不是整个测试集。

对于每个关系，我们构建一个关系层级记录，并比较不同映射类型组之间的多重性相关指标分布。

具体流程为：

1. 对每个关系计算指标
2. 为每个关系分配映射类型
3. 在不同映射类型之间比较指标分布

相比直接将同一类型的所有查询合并为一个全局数值，这种方法更符合论文叙事，也能避免少数大规模关系主导整体结果。

## 查询构建（Query Construction）

对于每个测试三元组 `(h, r, t)`，标准链接预测评估会生成：

* 一个头预测查询：`(?, r, t)`
* 一个尾预测查询：`(h, r, ?)`

因此，如果关系 `r` 在测试集中出现 `n_r` 次，则其贡献为：

* `n_r` 个头查询
* `n_r` 个尾查询
* 共 `2n_r` 个查询

## 支持变量（Support Variables）

为了提高统计结果的可解释性，我们显式记录支持变量。

### `test_support`

`test_support(r)` 表示关系为 `r` 的测试三元组数量。

### `head_support`

`head_support(r)` 表示由关系 `r` 生成的头预测查询数量。

在标准评估协议下，其值等于 `test_support(r)`。

### `tail_support`

`tail_support(r)` 表示由关系 `r` 生成的尾预测查询数量。

在标准评估协议下，其值也等于 `test_support(r)`。

### `eligible_support`

`eligible_support(r)` 表示满足以下条件的关系特定查询数量：

> 至少有一个输出命中 hits@k

该变量非常重要，因为多重性指标 `alpha_r` 和 `delta_r` 是在该子集上计算的，而不是在所有查询上计算。

## 为什么使用“至少一个输出命中 hits@k”的条件

当前多重性分析流程遵循 `Multiplicity_rewrite/main.py` 中已有的逻辑。

对于某个查询，如果所有输出都未命中 `hits@k`，则该查询被视为“统一失败”的情况，而非“模型间存在分歧”的情况，因此会从多重性分析子集中排除。

因此，多重性分析聚焦于那些“存在成功预测可能性”的查询。

这使得 `alpha_r` 和 `delta_r` 的解释更加明确：

* 它们描述的是在“可能成功”的查询上，不同输出之间的分歧
* 而不是对所有查询的整体错误率描述

## 关系层级指标（Relation-Level Metrics）

当前阶段，关系层级表中保留以下核心指标：

* `hits_r`
* `alpha_r`
* `delta_r`

在当前主线设计中，`epsilon_r` 不作为必须字段。

### `hits_r`

`hits_r` 表示关系 `r` 在多重性评估中，各个输出的 `Hits@k` 平均表现。

可以有两种计算方式：

* 将头查询和尾查询合并计算
* 分别保留头侧与尾侧结果

对于关系层级汇总表，使用合并版本是可以接受的，但建议在中间结果中保留头侧与尾侧信息，因为映射类型具有方向性。

### `alpha_r`

`alpha_r` 表示关系层级的歧义度（ambiguity score）。

它是在 eligible 子集上计算的，即仅考虑那些至少有一个输出命中 `hits@k` 的查询。

操作定义为：

当一个查询满足以下条件时，会对歧义度产生贡献：

* 至少一个输出命中 hits@k
* 并且不同输出之间在命中/未命中上存在分歧

因此，`alpha_r` 衡量的是：在 top-k 成功判定上，不同输出之间产生分歧的频率。

### `delta_r`

`delta_r` 表示关系层级的不一致度（discrepancy score）。

它同样是在与 `alpha_r` 相同的 eligible 子集上计算的。

操作定义为：

`delta_r` 衡量的是：参考输出与其他任意输出之间，在 hit/miss 判定上的最大分歧比例。

该定义沿用了当前代码中的实现逻辑，而非重新设计的新定义。

## 推荐的关系层级表结构

当前推荐的关系层级表包含以下字段：

* `relation_id`
* `relation_name`
* `mapping_type`
* `test_support`
* `head_support`
* `tail_support`
* `eligible_support`
* `hits_r`
* `alpha_r`
* `delta_r`

该表是连接多重性评估代码与映射类型分析的核心桥梁。

## 解释原则（Interpretation Principle）

建议的解释路径为：

* 首先比较不同映射类型（`1-1 / 1-N / M-1 / M-N`）之间的关系层级指标分布
* 然后分析某些映射类型是否系统性地对应更高的多重性

论文中应避免过强的因果性表述。当前阶段更稳妥的表述方式是：

> 映射类型是一种具有可解释性的结构性因素，与不同的多重性表现相关联。

## Symmetry Family

### 基本定位

与 `inverse` 不同，`symmetry` 是单个 relation 自身的结构属性，而不是由 relation pair 诱导出的属性。

如果某个 relation `r` 具有较强对称性，那么在训练图中：

* `(h, r, t)` 出现时
* `(t, r, h)` 也往往出现

因此，symmetry family 很适合直接沿用当前 thesis 的 relation-level 主分析单位。

也就是说，这一节最终仍然保持：

> 每个 relation 一行，再分析其 symmetry 特征与 relation-level multiplicity 指标之间的关系。

### 训练图定义

记训练图为：

```math
\mathcal{G}_{train} \subseteq \mathcal{E} \times \mathcal{R} \times \mathcal{E}
```

其中：

* `\mathcal{E}` 为实体集合
* `\mathcal{R}` 为关系集合

对任意 relation `r`，定义其边集合：

```math
E_r = \{(h,t) \mid (h,r,t) \in \mathcal{G}_{train}\}
```

这里的 `E_r` 是 relation `r` 在训练图上的有向实体对集合。

### Symmetric-Supported Edge Set

对任意 relation `r`，定义其对称支持子集为：

```math
E_r^{sym} = \{(h,t) \in E_r \mid (t,h) \in E_r\}
```

其含义是：

> 在 relation `r` 的所有训练事实中，那些能够在同一 relation 下找到反向事实支持的有向边。

这里要特别说明：

* `|E_r^{sym}|` 按有向边计数
* 如果 `(h,t)` 与 `(t,h)` 都存在，则它们都会分别计入 `E_r^{sym}`

因此，这个量不是 unordered pair count，而是：

* symmetric-supported directed edge count

### Relation-Level Symmetry Score

对每个 relation `r`，定义其 symmetry score 为：

```math
\operatorname{Sym}(r) = \frac{|E_r^{sym}|}{|E_r|}
```

也可写为：

```math
\operatorname{Sym}(r) =
\frac{|\{(h,t)\in E_r \mid (t,h)\in E_r\}|}{|E_r|}
```

其含义是：

> relation `r` 的所有训练事实中，有多大比例具有同关系下的反向支持。

这个量天然取值于 `[0,1]`：

* `0`：完全没有观察到同关系下的反向支持
* `1`：所有边都能找到反向对应，表现为完全对称
* 中间值：部分对称

### Self-Loop 问题

对于 self-loop 事实 `(h, r, h)`，其反向仍然是自己，因此会天然满足对称支持条件。

这一点在理论上需要显式记录。

在本项目的第一轮 symmetry sanity check 中，self-loop 被证明确实会显著污染部分 relation 的 raw symmetry score。

因此，当前推荐的口径是：

* raw `\operatorname{Sym}(r)` 保留为诊断性定义
* 主分析使用排除 self-loop 的版本

即定义：

```math
E_r^{sym,\neg loop} =
\{(h,t) \in E_r \mid h \neq t,\ (t,h) \in E_r\}
```

以及：

```math
E_r^{\neg loop} = \{(h,t) \in E_r \mid h \neq t\}
```

再定义主分析变量：

```math
\operatorname{Sym}^{\neg loop}(r) =
\frac{|E_r^{sym,\neg loop}|}{|E_r^{\neg loop}|}
```

当 `|E_r^{\neg loop}| = 0` 时，当前实现约定：

* `\operatorname{Sym}^{\neg loop}(r) = 0`

因此，在后续 symmetry section 中，更推荐把：

* `symmetry_score_excluding_self_loops`

作为主分析指标。

### 为什么当前不单独定义 Antisymmetry

当前阶段不建议把：

* 低 symmetry

直接写成：

* antisymmetry

原因是：

* `1 - Sym(r)` 只表示缺少对称支持
* 但严格的 antisymmetry 是更强的数学性质
* 许多 relation 只是 non-symmetric，并不满足严格的反对称定义

因此，在当前 thesis 设定里：

* 主分析变量是 `symmetry_score`
* 不把 `1 - symmetry_score` 当作正式的 `antisymmetry_score`

这可以避免概念上把：

* asymmetry / lack of symmetry

误写成：

* antisymmetry

### 与 Multiplicity 的关系

symmetry family 的温和主假设可以写为：

> stronger symmetry support may be associated with lower predictive multiplicity severity.

更具体地说，如果某个 relation 在训练图中具有更强的内部双向支持，那么 repeated runs 可能更容易学到相似的 ranking behavior，因此 relation-level multiplicity 可能更低。

但当前阶段更稳妥的表述仍然应当保持为：

* 结构关联
* 而不是强因果律

因此，更安全的 thesis wording 是：

> symmetry score is an interpretable single-relation structural factor that may be associated with multiplicity severity.

### 推荐的 Symmetry Relation-Level 表结构

当前推荐的 symmetry relation-level 表至少包含：

* `relation_id`
* `relation_name`
* `train_support`
* `self_loop_count`
* `symmetric_supported_edge_count`
* `symmetry_score_raw`
* `symmetry_score`

在与 multiplicity 表 merge 之后，主分析表至少包含：

* `relation_id`
* `relation_name`
* `train_support`
* `symmetry_score`
* `test_support`
* `hits_r`
* `alpha_r`
* `delta_r`

### 当前最小可运行版本

在 symmetry family 的第一轮实验中，最小可运行版本应当只包含：

1. 基于训练图计算每个 relation 的 raw symmetry score 与 excluding-self symmetry score
2. 与当前 relation-level multiplicity 表做 join
3. 做分布 sanity check
4. 做相关性和分桶分析

当前不建议一开始就扩展到：

* strict antisymmetry
* head-tail side-gap analysis
* 复杂回归控制

这些都应放在 symmetry 第一轮结果出现之后，再决定是否值得继续扩展。

## Inverse Family

### 基本定位

与 `mapping type` 或 `symmetry` 不同，`inverse` 天然不是单个 relation 的孤立属性，而是由 relation pair 诱导出来的结构关系。

如果：

* `(h, r_1, t)` 成立
* 且 `(t, r_2, h)` 也往往成立

那么 `r_2` 可以被视为 `r_1` 的潜在 inverse partner。

但整篇 thesis 的分析单位仍然保持为单个 relation。因此，在 inverse 这一节中，我们不直接把 relation pair 当作最终样本单位，而是：

> 先从 relation pair 中提取 inverse evidence，再将其压缩为单个 relation 的结构特征。

### 训练图定义

记训练图为：

```math
\mathcal{G}_{train} \subseteq \mathcal{E} \times \mathcal{R} \times \mathcal{E}
```

其中：

* `\mathcal{E}` 为实体集合
* `\mathcal{R}` 为关系集合

对任意 relation `r`，定义其边集合：

```math
E_r = \{(h,t) \mid (h,r,t) \in \mathcal{G}_{train}\}
```

定义其反向边集合：

```math
E_r^{rev} = \{(t,h) \mid (h,r,t) \in \mathcal{G}_{train}\}
```

所有 inverse-related 结构统计都只基于训练图计算，不使用验证集或测试集信息。

### Pair-Level Directional Inverse Score

对任意 relation pair `(r_1, r_2)`，定义方向性的 inverse score：

```math
s(r_1 \to r_2) = \frac{|E_{r_1} \cap E_{r_2}^{rev}|}{|E_{r_1}|}
```

其含义是：

> `r_1` 的事实中，有多大比例能够在 `r_2` 中找到反向对应事实。

这是一个方向性定义，因此一般不要求：

```math
s(r_1 \to r_2) = s(r_2 \to r_1)
```

在当前项目中，这个量可以更明确地命名为：

* `directional_inverse_score`

它是后续更严格 inverse-like 指标族的基线版本。

### Relation-Level Directional Inverse Strength

为了继续保持 relation-level 主线，我们对每个 relation `r` 定义：

```math
\operatorname{DirInvStrength}(r) = \max_{r' \in \mathcal{R}, r' \neq r} s(r \to r')
```

其含义是：

> 在所有其他 relation 中，哪个 relation 最像 `r` 的 inverse partner，以及这种 inverse support 有多强。

同时定义：

```math
\operatorname{BestDirInvPartner}(r) = \arg\max_{r' \in \mathcal{R}, r' \neq r} s(r \to r')
```

在第一轮实验中，代码与结果文件中使用的：

* `inverse_strength`
* `best_inverse_partner`

本质上就对应这里的：

* `directional_inverse_strength`
* `directional_best_inverse_partner`

也就是说，第一轮 inverse section 实际上是：

* one-sided reverse-overlap baseline

而不是严格意义上的双向 inverse 指标。

### 为什么需要更严格的 Inverse-Like 指标

第一轮 directional 定义在理论上成立，但在经验上可能混入：

* reverse containment
* broad relation coverage
* general reverse overlap

也就是说，如果某个较窄 relation 的事实大多包含在某个更宽 relation 的反向边集中，那么 directional score 仍可能很高，即使这个 pair 并不是理想的 mutual inverse。

因此，在第二轮实验中，需要引入更严格的 inverse-like metric family。

### Pair-Level Mutual Inverse Score

对任意 relation pair `(r_1, r_2)`，定义双向支持：

```math
s_{12} = s(r_1 \to r_2), \qquad s_{21} = s(r_2 \to r_1)
```

再定义其 harmonic-mean mutual score：

```math
s_{\mathrm{mut}}(r_1, r_2) =
\begin{cases}
\frac{2 s_{12} s_{21}}{s_{12} + s_{21}}, & s_{12} + s_{21} > 0 \\
0, & \text{otherwise}
\end{cases}
```

其含义是：

> 只有当两边都存在较强反向支持时，pair-level inverse-like score 才会高。

这个定义比 directional score 更严格，因为它显式惩罚：

* 单边高、另一边低的情况

因此更适合区分：

* genuinely mutual inverse-like pairs

和：

* one-sided containment or asymmetric reverse overlap

### Pair-Level Overlap Jaccard

在第二轮实验中，还记录一个辅助的 pair-level 集合相似度：

```math
s_J(r_1, r_2) = \frac{|E_{r_1} \cap E_{r_2}^{rev}|}{|E_{r_1} \cup E_{r_2}^{rev}|}
```

其作用不是作为主分析变量，而是用于辅助判断：

* pair 的重叠是否不仅仅来自一侧 support 很小
* pair 的集合相似度是否足够高

因此，`overlap_jaccard` 更适合：

* sanity check
* pair-level case study

而不是作为 thesis 主统计量。

### Relation-Level Mutual Inverse Strength

为了继续保持 relation-level 分析单位，对每个 relation `r` 定义：

```math
\operatorname{MutInvStrength}(r) =
\max_{r' \in \mathcal{R}, r' \neq r} s_{\mathrm{mut}}(r, r')
```

并定义：

```math
\operatorname{BestMutInvPartner}(r) =
\arg\max_{r' \in \mathcal{R}, r' \neq r} s_{\mathrm{mut}}(r, r')
```

这个变量在代码与结果文件中记为：

* `mutual_inverse_strength`
* `mutual_best_inverse_partner`

与第一轮 directional baseline 相比，它更适合作为：

* stricter inverse-like relation-level proxy

### Relation-Level Inverse Clarity

即使一个 relation 的 best mutual partner 分数较高，也仍可能存在一个问题：

* 它并不是只和一个 partner 高度匹配
* 而是同时和多个 relation 都有相近的 reverse overlap

因此，在第二轮实验中，对每个 relation `r` 进一步定义：

* `best mutual score`
* `second-best mutual score`

并构造：

```math
\operatorname{InvClarity}(r) =
\max\bigl(0,\ \operatorname{MutInvStrength}(r) - \operatorname{SecondBestMutInvStrength}(r)\bigr)
```

其含义是：

> relation `r` 的最佳 mutual inverse partner 是否明显优于第二候选。

这个变量在代码与结果文件中记为：

* `inverse_clarity`

它的解释重点不是“inverse 有多强”，而是：

* inverse partner 是否足够明确

因此：

* `mutual_inverse_strength` 回答“最强 partner 有多强”
* `inverse_clarity` 回答“最强 partner 是否足够独特”

### 推荐的 Inverse-Like 指标体系

在当前 thesis 语境下，inverse family 更稳妥的定义应当理解为一个指标族，而不是单个数字。

推荐保留三层：

1. `directional_inverse_strength`
   作为第一轮 one-sided reverse-overlap baseline
2. `mutual_inverse_strength`
   作为更严格的双向 inverse-like proxy
3. `inverse_clarity`
   作为 best-partner uniqueness / confidence proxy

辅助变量还包括：

* `best partner`
* `second-best partner`
* `overlap_count`
* `overlap_jaccard`

其中 thesis 主分析更适合聚焦：

* `mutual_inverse_strength`
* `inverse_clarity`

而将 `directional_inverse_strength` 保留为对照基线。

### 与 Multiplicity 的关系

inverse family 的第一轮朴素假设可以表述为：

> stronger inverse structural support is expected to be associated with lower predictive multiplicity.

但在当前项目推进后，更稳妥的理论表述应调整为：

> high-confidence inverse-like support may be associated with lower predictive multiplicity, but the effect need not be global or monotonic.

也就是说，如果一个 relation 在训练图中拥有：

* 较强的双向 reverse support
* 且较清晰的唯一 partner

那么不同 repeated runs 可能更容易收敛到相对一致的 ranking behavior，因此 relation-level multiplicity severity 可能更低。

但当前不应再把这件事表述为：

* “所有 inverse support 越强的 relation 都更稳定”

当前阶段更稳妥的表述仍然是“结构关联”而不是强因果论断。即：

> inverse-like support is an interpretable relation-level structural factor family that may be associated with multiplicity severity, especially for high-confidence subgroups.

### 第一轮实验建议

在 inverse family 的第一轮实验中，建议优先做最小可运行版本：

1. 只计算 direction-based `inverse_strength`
2. 先做 sanity check，不急着做复杂统计控制
3. 先与当前 relation-level multiplicity 表做 join
4. 先做相关性与分桶分析

更严格的 mutual inverse 定义、回归控制与案例分析可以放在后续增强阶段。

### 第二轮实验建议

在第一轮 directional baseline 之后，第二轮更合理的增强步骤是：

1. 保留 `directional_inverse_strength` 作为基线
2. 加入 `mutual_inverse_strength`
3. 加入 `inverse_clarity`
4. 继续与 relation-level multiplicity 表做 join
5. 优先检查 high-confidence subgroup，而不只依赖全局 Spearman

当前理论上最稳妥的 thesis 立场是：

* inverse 不是全局单调解释变量
* 但 stricter inverse-like metrics 可能识别出更稳定的小规模 subgroup

## 下一步工作

下一步的重点不是重新设计理论，而是让代码能够导出上述定义的关系层级表。

## 配套实验记录

本文件只保留相对稳定的理论定义与指标口径。

与当前 mapping type 分析相关的实验设置、运行流程、中间结果与阶段性结论，单独记录在：

- `Research/thesis_mapping_type_experiment.md`

与当前 inverse 分析相关的实验设置、运行流程、中间结果与阶段性结论，单独记录在：

- `Research/thesis_inverse_experiment.md`

这样做的原因是：

* 理论定义应尽量保持稳定
* 实验过程与结果会持续更新
* 将两者分开更利于后续论文整理与版本维护
