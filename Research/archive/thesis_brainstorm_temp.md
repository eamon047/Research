# Relation Frequency：理论定位、数理定义与实验设计整理

## 1. 这一节在 thesis 里的定位

这一节的核心不是把 `relation frequency` 硬写成一个新的 `relation pattern`，而是把它放在一个更准确的位置：

> `relation frequency` 是一个 **relation-level support / sparsity factor**，而不是一个典型的 structural pattern。

因此，在整篇 thesis 中，更推荐将 relation-level 因素分成两类：

### A. Pattern-like structural factors
这类因素描述的是 relation 的结构形式或逻辑形式：

- `mapping type`
- `inverse-like support`
- `symmetry`

### B. Support / sparsity factors
这类因素描述的是 relation 在训练图中的支持度、数据丰富程度或稀疏性：

- `relation frequency`

因此，`relation frequency` 不建议与 `mapping type / inverse / symmetry` 并列写成“四个 relation pattern”，而更适合写成：

> 本文分析 relation patterns，并引入 relation frequency 作为一个基线的 support / sparsity control variable。

---

## 2. 为什么 frequency 值得做？

这部分并不是凭空补出来的。

在 Zhu et al. (2024) 中，作者在 Section 6.2.3 明确分析了 `entity/relation frequency` 与 predictive multiplicity 之间的关系。他们将 entity/relation frequency 定义为包含该 entity/relation 的三元组数量，然后用 Spearman 相关检验其与 empirical ambiguity 和 discrepancy 的关系，得到显著负相关的结果。

其中，relation frequency 的相关性比 entity frequency 更强，因此对于当前 thesis 这种 **relation-level analysis** 来说，relation frequency 是一个非常自然、而且有文献支撑的基线变量。

但是，在你的 thesis 中，这一节的目标不是“重复原文结论”，而是：

1. 在你自己的固定 thesis 设定下重新验证 relation frequency
2. 用 relation frequency 作为解释 mapping type 结果的参照轴
3. 检查 mapping type 的效应是否只是 frequency 的影子
4. 为 inverse / symmetry 这些 mixed 或 weak 结果提供一个 support-level 的解释框架

因此，这一节最好的定位是：

> 验证性复现 + 控制变量分析 + 结果解释框架

而不是：

> 一个全新的 pattern 发现

---

## 3. 和原文相比，你这一节的“自己的内容”在哪里？

原文的 frequency 分析是一个更宽的全局统计：

- 同时分析 entity frequency 与 relation frequency
- 跨多个模型
- 跨多个数据集
- 主要给出全局 Spearman 结果

而你的 thesis 已经明确收缩到了：

- 数据集：`FB15k-237`
- 模型：固定 repeated runs 的 thesis setting
- 分析单位：`relation-level`
- 主目标：解释 relation-level multiplicity 的结构差异

所以，你这一节的“自己的内容”不在于重新发明 frequency，而在于：

### 你的重定位
你把原文中的 frequency，从一个全局 supplementary factor，重新放进了你自己的 relation-level thesis framework 中，并且主要用来回答下面这些问题：

1. 在当前 thesis 固定设定下，relation frequency 是否仍然和 multiplicity 有关？
2. mapping type 的主结果是否在考虑 frequency 后仍然存在？
3. inverse / symmetry 为什么没有形成主结果，是否和 relation sparsity 有关？

这就不是“照抄”，而是**在你自己的分析框架中重新使用一个已有但必要的变量**。

---

## 4. 这一节最推荐的 thesis 叙事

最稳的叙事不是：

> 本文研究了四个 relation pattern：mapping type、inverse、symmetry 和 frequency

而是：

> 本文主要研究 relation-level 的结构模式（mapping type、inverse-like support、symmetry）与 predictive multiplicity 的关系；同时引入 relation frequency 作为一个 support-level 基线变量，用于验证低支持关系是否更易出现 multiplicity，并用于检验 mapping type 的作用是否独立于简单的稀疏性效应。

这个写法更准确，也更不容易被追问概念问题。

---

## 5. 数理定义

### 5.1 训练图定义

记训练图为：

```math
\mathcal{G}_{train} \subseteq \mathcal{E} \times \mathcal{R} \times \mathcal{E}
```

其中：

- `\mathcal{E}` 为实体集合
- `\mathcal{R}` 为关系集合

### 5.2 Relation Frequency

对任意 relation `r \in \mathcal{R}`，定义其 relation frequency 为：

```math
\operatorname{Freq}(r) = |\{(h,r,t) \in \mathcal{G}_{train}\}|
```

其含义是：

> 训练图中，relation `r` 出现的三元组数量。

### 5.3 为什么优先使用训练集中的 frequency？

和其他 pattern 特征一样，这里建议只用训练图统计 frequency，而不要把验证集或测试集也加进去。

原因：

- 这样和 mapping type / symmetry / inverse 的定义口径一致
- 避免“用测试信息定义结构变量”的嫌疑
- 更符合 thesis 里“所有 pattern / factor 均来自 training graph”的统一逻辑

---

## 6. relation frequency 的解释边界

这一点很重要。

`relation frequency` 本身不是 relation 的逻辑性质，也不是几何 pattern。它描述的是：

- 这个 relation 在训练图中被观察到多少次
- 因而在训练中受到多少事实约束
- embedding 学习时有多少支持数据

因此，它更像：

- support
- sparsity
- data richness
- constraint strength

而不是：

- symmetry
- inversion
- composition
- mapping form

所以这一节的语言要刻意避免：

- “frequency pattern”
- “frequency family”

更好的叫法是：

- relation frequency factor
- support variable
- sparsity-related factor
- baseline structural control

---

## 7. 核心假设怎么写？

### H1：基线支持度假设
**relation frequency 越低的 relation，可能越容易出现更高的 predictive multiplicity。**

直觉是：

- 低频 relation 在训练中受约束更少
- embedding 存在更大的不确定性空间
- repeated runs 更可能学到不完全一致的 decision boundary / ranking behavior
- 因而 `alpha_r`、`delta_r` 可能更高

这个直觉与 Zhu et al. 的解释是一致的。

### H2：mapping type 独立性问题
**mapping type 的效应是否独立于 relation frequency？**

也就是说，我们进一步要问：

> 当前 mapping type 的主结果，是不是只是某些 mapping type 恰好更高频 / 更低频造成的？

这一问非常关键，因为它能把 frequency 和 mapping type 联系起来，而不是让 frequency 变成一节孤立的小分析。

### H3：解释 mixed / weak 结果
**inverse / symmetry 之所以没有形成 clean 主结果，是否部分源于它们与 relation support / sparsity 纠缠在一起？**

这个假设不需要强行做成大规模多变量模型，但非常适合在 discussion 里作为解释框架使用。

---

## 8. 实验设计：建议分三层做

---

### 第一层：验证性 relation-level frequency analysis

这是最基础的一层。

#### 输入
- 训练集 triples
- 现有 relation-level multiplicity 表

#### 计算
对每个 relation `r` 统计：

- `relation_frequency`
- `hits_r`
- `alpha_r`
- `delta_r`
- `test_support`

#### 分析
优先计算 Spearman correlation：

- `log_freq_r` vs `hits_r`
- `log_freq_r` vs `alpha_r`
- `log_freq_r` vs `delta_r`

这里建议直接使用：

```math
\log(\operatorname{Freq}(r)+1)
```

而不是裸频率。

原因：

- 频率分布通常高度长尾
- 对数变换后更容易看趋势
- 作图也更稳定

#### 预期
- `log_freq_r` 和 `alpha_r` 负相关
- `log_freq_r` 和 `delta_r` 负相关
- `log_freq_r` 和 `hits_r` 可能正相关，但这不是主角

#### 输出文件建议
- `relation_frequency_stats.csv`
- `relation_frequency_multiplicity_merged.csv`
- `correlation_stats.csv`
- `bucket_stats.csv`
- `analysis_summary.txt`

---

### 第二层：把 frequency 与 mapping type 放在一起看

这层才最有 thesis 味。

因为你当前最强的结果是 mapping type，所以 frequency 的真正价值在于：

> 检查 mapping type 的效应是否只是 frequency 的影子。

#### 做法 A：mapping type 内部分层分析
在每个 `mapping_type` 内，再计算：

- `log_freq_r` vs `alpha_r`
- `log_freq_r` vs `delta_r`
- `log_freq_r` vs `hits_r`

这样可以回答：

- 频率效应是否在所有 mapping type 中都存在？
- 某些 mapping type 是否特别依赖 support？
- 某些 mapping type 的 multiplicity 是否即使在高频下也仍然偏高？

#### 做法 B：简单控制分析
最简单的控制形式可以是一个小回归：

```math
\alpha_r \sim \log(\operatorname{Freq}(r)+1) + \operatorname{MappingType}(r)
```

```math
\delta_r \sim \log(\operatorname{Freq}(r)+1) + \operatorname{MappingType}(r)
```

如果不想走回归，也可以做更轻量的版本：

- 先把 relation frequency 分桶
- 再在每个 frequency bucket 里比较不同 mapping type 的 `alpha_r / delta_r`

#### 这一层的目标
不是证明 frequency 比 mapping type 更重要，而是：

> 证明 mapping type 的主结果不是一个纯粹的频率假象。

这点对 thesis 非常重要。

---

### 第三层：把 frequency 作为解释 inverse / symmetry 的参照轴

这一层不是必须做大量统计，但建议至少做最简单的辅助检查。

#### 对 inverse
你已经发现 inverse 的信号是 mixed / non-monotonic 的。  
这时 frequency 可以帮你问：

- inverse 高置信 subgroup 是否集中在高频 relation？
- middle ambiguous bucket 是否恰好也是中低频 relation 的聚集区？

#### 对 symmetry
你已经发现高 symmetry relation 几乎全在 `M-N`，而且结果并不好。  
这时 frequency 也可以帮你问：

- high-symmetry subgroup 是否也在 relation support 上高度偏置？
- symmetry 的弱结果是否部分源于 support + structure entanglement？

这一步不需要把 inverse / symmetry 全都再重做一轮，只要补一些 summary table 或 case-level 对比，就已经很有解释力。

---

## 9. 具体实施步骤

### Step 1：从训练图提取 relation frequency

输入：`train.txt`

输出：`relation_frequency_stats.csv`

字段建议至少包含：

- `relation_id`
- `relation_name`
- `train_frequency`
- `log_train_frequency`

---

### Step 2：与 relation-level multiplicity 表 merge

把 `relation_frequency_stats.csv` 和你现在的主表 merge，形成：

`relation_frequency_multiplicity_merged.csv`

字段建议至少包含：

- `relation_id`
- `relation_name`
- `train_frequency`
- `log_train_frequency`
- `mapping_type`
- `test_support`
- `hits_r`
- `alpha_r`
- `delta_r`

如果你愿意，后面还能继续接：

- `inverse_strength`
- `mutual_inverse_strength`
- `inverse_clarity`
- `symmetry_score_excluding_self_loops`

但第一轮 frequency 不必强行全加。

---

### Step 3：做相关分析

优先做 Spearman：

- `log_train_frequency` vs `hits_r`
- `log_train_frequency` vs `alpha_r`
- `log_train_frequency` vs `delta_r`

最好至少分两版 support filter：

- all relations
- `test_support >= 5`
- `test_support >= 10`

这样和你 inverse / symmetry 的分析口径也比较一致。

---

### Step 4：做分桶分析

建议按 `log_train_frequency` 的分位数分桶，而不是硬编码阈值。

例如：

- low frequency
- medium frequency
- high frequency

或 quartiles / tertiles。

然后比较每个桶的：

- `mean hits_r`
- `mean alpha_r`
- `mean delta_r`

这是 thesis 里最好讲故事的一种图。

---

### Step 5：做 mapping type × frequency 联合分析

两种最稳做法：

#### 方案 A：每个 mapping type 内看 frequency 相关性
输出文件例如：

- `correlation_by_mapping_type.csv`
- `bucket_stats_by_mapping_type.csv`

#### 方案 B：frequency bucket 内看 mapping type 差异
例如：

- 在 low-frequency subgroup 内，不同 mapping type 的 `alpha_r / delta_r` 是否仍有明显差异？
- 在 high-frequency subgroup 内，mapping type 的差异是否缩小或仍然存在？

如果 mapping type 在不同 frequency strata 下仍然稳，那你就有一个很强的 thesis 句子：

> mapping type is not merely a proxy for relation frequency.

---

## 10. 推荐图表

### 必做图

#### 图 1：log frequency vs alpha
- 横坐标：`log_train_frequency`
- 纵坐标：`alpha_r`
- 图形：散点图 + 趋势线

#### 图 2：log frequency vs delta
- 横坐标：`log_train_frequency`
- 纵坐标：`delta_r`
- 图形：散点图 + 趋势线

---

### 推荐图

#### 图 3：frequency bucket 的均值图
- 横坐标：frequency buckets
- 纵坐标：
  - `mean alpha_r`
  - `mean delta_r`
  - optional `mean hits_r`

#### 图 4：mapping type × frequency bucket 联合图
例如：

- 每个 frequency bucket 内，不同 mapping type 的 `mean alpha_r / delta_r`

这个图非常适合 thesis，因为它能把你最强的主结果（mapping type）和最稳的 control variable（frequency）放在一起。

---

## 11. 这一节的最佳论文写法

### 不推荐写法
- frequency 是第四个 relation pattern
- 我们又发现了一个新的 pattern

### 推荐写法
- relation frequency is included as a baseline support variable
- it serves as a control and reference axis for relation-level pattern analysis
- it helps distinguish pattern effects from simple sparsity effects

中文可以写成：

> 除 relation patterns 外，本文进一步引入 relation frequency 作为一个 relation-level 的支持度变量。其作用并非作为新的逻辑模式，而是作为基线控制因素，用于检验低支持关系是否更易出现 predictive multiplicity，并进一步考察 mapping type 的效应是否独立于简单的稀疏性差异。

---

## 12. 可以直接用于论文的方法段落

### 中文版

本文在 relation-level pattern analysis 之外，引入 relation frequency 作为一个基线支持度变量。对于每个 relation `r`，其 frequency 定义为训练图中包含该 relation 的三元组数量。考虑到该变量在知识图谱中通常呈长尾分布，本文使用 `log(freq(r)+1)` 作为主要分析形式。该变量不被视为 relation pattern 本身，而被视为 support / sparsity factor，用于检验低支持关系是否更易出现 predictive multiplicity，并用于分析 mapping type 的作用是否独立于简单的稀疏性效应。

### 英文版

In addition to relation patterns, we include relation frequency as a baseline support variable in our relation-level analysis. For each relation `r`, its frequency is defined as the number of training triples containing `r`. Since this variable typically exhibits a heavy-tailed distribution in knowledge graphs, we use `log(freq(r)+1)` as the main analytical form. We do not treat relation frequency as a relation pattern itself, but rather as a support / sparsity factor, which allows us to examine whether low-support relations are more multiplicity-prone and whether the effect of mapping type remains after accounting for simple sparsity differences.

---

## 13. 最小可运行版本（推荐优先实现）

如果当前希望尽快把这一节补进 thesis，而不把工程量做大，建议先只做下面四步：

1. 计算每个 relation 的 `train_frequency` 和 `log_train_frequency`
2. merge 到 relation-level multiplicity 表
3. 输出：
   - `log_train_frequency vs alpha_r`
   - `log_train_frequency vs delta_r`
4. 再做一个最基础的 `mapping_type × frequency` 联合 summary

只要这四步做完，这一节就已经足够支撑 thesis 里的一个完整 subsection。

---

## 14. 一句话总结

`relation frequency` 最适合在本文中被定位为：

> **一个 relation-level 的 support / sparsity factor，用于作为基线控制变量和解释参照轴，而不是作为一个新的 relation pattern。**
