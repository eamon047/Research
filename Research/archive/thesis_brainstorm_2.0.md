# Thesis Brainstorm 2.0

## Background

这份文档用于整理当前毕业论文方向的第二轮头脑风暴。

与 `Thesis Brainstorm 1.0` 相比，这一版不再把“模型选择器”作为默认主线，
而是将研究目标收缩到一个更适合毕业论文、风险更低、也更容易讲清楚故事的方向：

> 不同 relation pattern 下，KGE 的 predictive multiplicity 是否存在系统性差异？

在这个主问题之上，如果时间和实验结果允许，再进一步讨论：

> 是否可以用更小规模的模型委员会，近似大规模 voting 的效果？


## Why 1.0 Was Not Ideal

`1.0` 的核心想法并不是错误，而是对毕业论文来说风险偏高。

当时的主线更接近：

- 不同 KGE 模型在不同结构模式下是否存在稳定优势
- 如果存在，能否为 relation 或 query 选择更合适的模型

这个方向的问题主要不在于“浅”，而在于它默认会把工作推向一个方法型问题：

- 需要先证明不同模型之间确实存在稳定、可重复的互补性
- 需要再设计一个 selector / router
- 需要最后证明这个 selector 真能稳定带来提升

这就会带来几个现实风险：

1. 很容易做成一个很大的工程系统，但最后提升并不稳定。
2. 如果模型间差异不够稳定，selector 会退化成一个解释困难的堆叠器。
3. 如果做到 query-level，问题会立刻变得更复杂，特征、噪声、评价方式都会膨胀。
4. 答辩时很容易被追问：“为什么不直接 ensemble？”“为什么这个选择器不是偶然有效？”

因此，`1.0` 更像一个“可能发展成更大工作”的方向，
但对当前“以顺利毕业为最高优先级”的目标来说，并不是最稳的主线。


## What Changed in 2.0

`2.0` 的关键变化是：把问题从“做模型选择”退回到“解释 multiplicity 为什么发生”。

这会带来几个直接好处：

- 更像分析型研究，技术风险更低
- 更容易依托现有复现工作继续推进，而不是另起一套系统
- 更容易形成一条清楚的论文叙事链
- 即使最后没有做出 fancy 的方法，也仍然可以形成完整论文

当前更稳的叙事是：

1. 先复现并确认 KGE 中确实存在 predictive multiplicity。
2. 再分析这种 multiplicity 是否在不同 relation pattern 下严重程度不同。
3. 如果这种差异确实存在，再顺势讨论 full voting 是否存在冗余，以及 small committee 是否可行。


## Core Thesis Question

当前建议作为毕业论文主问题的是：

> 不同 relation pattern 下，KGE 的 predictive multiplicity 是否存在系统性差异？

更具体地说，可以把这个问题拆成三层：

1. 同一个 KGE 模型在 repeated runs 下，是否会对某些 relation 表现出更高的预测分歧？
2. 这种分歧程度是否与 relation 的结构特征有关？
3. 不同模型家族的 multiplicity profile 是否不同？

如果前面结果成立，再补一个扩展问题：

4. 给定一个已有模型池，是否可以用少量模型近似 full voting 的效果？


## Scope

为了控制工作量，当前建议把范围严格限制在下面这些内容里。

### Main Setting

- 主分析粒度：`relation-level`
- 暂不做：`query-level` selector / router
- 主数据集：`FB15k-237`
- 第二阶段可选数据集：`WN18RR`

### Main Models

第一阶段只保留：

- `TransE`
- `RotatE`

第二阶段再补：

- `ComplEx`

这样做的原因是：

- `RotatE` 和 `TransE` 已经有比较清楚的 repeated runs 基础
- 先做两类风格差异较明显的模型，更容易看出结构差异
- `ComplEx` 适合作为增强验证，而不是一开始就扩大工作面


## Main Patterns

relation pattern 当前建议只保留 4 个核心维度：

1. `mapping type`
2. `symmetry / antisymmetry`
3. `inverse relation strength`
4. `answer cardinality`

选择这四个维度的原因是：

- 都能从图结构直接计算
- 都容易解释
- 都和 KGE 模型表达能力或优化难度有自然联系
- 很适合作为毕业论文中的主分析变量

当前不建议优先做的维度包括：

- path composition
- query difficulty
- local structural support
- dynamic routing features

这些不是没价值，而是更适合后续扩展，不适合当前第一主线。


## Main Metrics

当前最重要的，不是堆太多 pattern，而是先把 multiplicity 的量化方式定稳。

建议至少定义两类指标：

### 1. Relation-Level Disagreement

描述同一个 relation 下，不同 repeated runs 的预测结果到底有多不一致。

可以考虑的实现方式包括：

- relation 内 top-k 预测集合重叠程度
- relation 内不同 run 的 Hits@10 波动
- relation 内 baseline 与 competing runs 的预测一致率

### 2. Relation-Level Voting Gain

描述在某个 relation 上，voting 相比 single model 是否真的带来收益。

可以考虑的实现方式包括：

- full voting 相比 best single run 的 Hits@10 提升
- full voting 相比 average single run 的提升

这里的原则是：

- 先做简单、稳定、好解释的定义
- 不要一开始就设计过于复杂的 multiplicity score


## Research Story

当前最适合毕业论文的叙事方式不是：

- “我们做了一个很聪明的模型选择器”

而是：

- “我们发现 predictive multiplicity 不是均匀分布的，而是和 relation structure 有关”

然后再补一句更务实的扩展：

- “既然 full voting 可能存在冗余，那么小规模 committee 值得进一步研究”

这个故事更稳，因为它把论文分成了主线和副线：

- 主线是分析与解释
- 副线是效率与实用性

这样即使副线结果不够漂亮，主线也仍然成立。


## About Voting Reduction

这里必须特别说明一个很容易混淆的问题。

“relation pattern 分析”与“voting 模型规模缩减”是相关的，但不应该一开始强绑定。

原因是：

- relation pattern 主要回答“为什么 multiplicity 会这样分布”
- voting 缩减主要回答“已有模型池里是否存在冗余”

如果直接说：

- multiplicity 高的 relation 用更多 voter
- multiplicity 低的 relation 用更少 voter

那么就会碰到一个现实问题：

- 为了做动态分配，你往往还是得先训练出足够大的模型池

这意味着：

- 它未必减少训练成本
- 它更像减少推理或使用阶段的冗余

因此当前更合理的做法是：

- 先把 voting reduction 当作一个独立扩展问题
- 不把它写成 relation pattern 分析的直接结论

更稳的表达方式是：

> 在已有模型池的前提下，full voting 可能存在冗余，因此 small committee 值得尝试。


## Minimal Viable Thesis

如果目标是“顺利毕业”，那么最小可毕业版本建议定义为：

- 数据集：`FB15k-237`
- 模型：`RotatE` + `TransE`
- repeated runs：每个模型至少 8 个
- pattern：4 个
- multiplicity 指标：2 个
- 输出：relation-level 分析表和可视化图

只要最后能够说明：

- 某些 relation pattern 下 multiplicity 更严重
- 这种现象在至少两个模型中都可观察
- 不同模型的 multiplicity profile 又不完全相同

那么论文主线就已经成立。


## Framework

当前建议的推进框架如下：

### Stage 1: Reproduction and Sanity Check

- 先把现有 repeated runs 的评估链路整理干净
- 明确当前 checkpoint 使用口径
- 确认 multiplicity 评估脚本能稳定输出结果

### Stage 1.5: Local Debugging Policy

在真正进入论文分析之前，当前已经额外形成一个更务实的本地推进原则：

- 先把 `Multiplicity` 主实验跑通
- 先不急着细化论文标题和 relation-pattern 统计分析
- 先不急着严格复现论文里的 baseline 选择与 `epsilon` 构造流程

这样做的原因是：

- 如果主评估链路不能稳定运行，后续研究问题和论文叙事都没有落点
- 当前 released code 更像研究原型，而不是可直接运行的本地脚本
- 当前阶段最需要的是“把实验资产真正接起来”，而不是继续扩展研究问题

### Stage 2: Relation Statistics

- 为每个 relation 计算结构特征
- 形成一个 relation-level 的统计表

### Stage 3: Multiplicity Analysis

- 为每个 relation 计算 multiplicity severity
- 比较不同 pattern 下的 severity 分布
- 比较不同模型的 multiplicity profile

### Stage 4: Optional Small Committee Study

- 在已有模型池中选择小规模子集
- 比较 full voting 与 small committee 的差异
- 只把这部分当扩展，不把它定义为主贡献


## To-Do List

### Must Do First

1. 最终确认论文主问题就是 relation pattern 与 multiplicity 的关系。
2. 明确只做 `relation-level`，不做 `query-level`。
3. 确定第一阶段只使用 `FB15k-237 + RotatE/TransE`。
4. 定义 4 个 relation pattern 指标。
5. 定义 2 个 multiplicity severity 指标。
6. 先把 `Multiplicity` 主实验脚本在本地环境中稳定跑通。

### Must Do Next

1. 整理 `RotatE_FB15k237` 的 repeated runs 输出。
2. 整理 `TransE_FB15k237` 的 repeated runs 输出。
3. 写 relation statistics 脚本。
4. 写 relation-level multiplicity analysis 脚本。
5. 输出第一版表格和图。

### Should Do After That

1. 补 `ComplEx`。
2. 做 small committee 的基础比较实验。
3. 如果结果稳定，再考虑补 `WN18RR`。

### Do Not Do Yet

1. 不做 query-level selector。
2. 不做 relation-aware dynamic committee size。
3. 不急着查其他领域 multiplicity 的解决方案。
4. 不急着尝试复杂 voting 规则。
5. 不要同时上太多模型和数据集。
6. 不要优先投入 `query_answering` 两个脚本。


## Current Working Assumptions

这是当前进入代码调试阶段后，额外明确下来的几条工作假设。

### 1. Current Priority

当前优先级已经进一步收缩为：

- 先跑通 `Multiplicity` 主实验
- 再讨论 relation pattern 与 multiplicity 的论文分析

也就是说：

- 现在优先处理的是“实验管线可运行性”
- 不是“方法设计”或“论文包装”

### 2. Strict Reproduction vs. Engineering Approximation

这里需要明确区分两种口径：

- 严格复现论文
- 工程上先跑通主实验

严格论文流程应当是：

1. 先确定 best baseline model
2. 再按 `epsilon` 构造 competing model set
3. 最后在这个近似 `epsilon`-level set 上评估 multiplicity

但当前 released `Multiplicity/main.py` 并没有严格实现这条流程。

它当前做的是：

- 读取一组已有 runs
- 从中随机抽样
- 然后直接在抽样结果上计算 `Hits / Epsilon / Alpha / Delta`

因此当前本地跑通的主实验，应理解为：

- 已有 repeated runs 上的 multiplicity evaluation pipeline

而不是：

- 严格复现论文中的 `S'ε(M*)` 构造过程

### 3. Current Debug Setting

在尽量少改源码的前提下，当前本地 debug 版本采用：

- 只跑一个组合
- 当前首选组合：`RotatE + FB15k-237`
- run 池规模：已有 `8` 个 seed
- 当前实验参数：`num = 7`, `agg_num = 7`, `k = 10`

这里的含义更接近：

- 在 7 个近似等价 run 上计算 multiplicity

而不是：

- 严格固定“1 个 best baseline + 6 个由 `epsilon` 过滤出的 competing models”

### 4. Query-Answering Scripts

当前不建议优先投入：

- `Multiplicity/query_answering_1.py`
- `Multiplicity/query_asnwering_10.py`

原因包括：

- 依赖额外的 score cache
- 发布代码中仍有作者机器路径和未清理的实现痕迹
- 其研究价值更适合后续扩展，而不是当前主线

当前论文与代码推进，先聚焦：

- link prediction 主实验


## Risk Control

当前最需要防止的，不是“想法太简单”，而是“问题做散”。

因此当前的控制原则应当是：

- 优先保住主线，而不是追求花哨扩展
- 优先做分析型结论，而不是过早做方法型系统
- 优先把定义和指标定稳，而不是急着加模型和数据集

如果中期发现：

- relation pattern 与 multiplicity 的关系不够稳定

那么可以及时收缩成：

> 不同 KGE 模型 predictive multiplicity 的经验分析，relation pattern 作为辅助解释变量

这仍然是一条可毕业的后备路线。


## One-Sentence Summary

`2.0` 版本的毕业论文主线应当是：

> 以 relation pattern 为切入点，分析 KGE predictive multiplicity 的结构性差异；在此基础上，再谨慎讨论 full voting 是否存在可压缩的冗余。


## Current One-Sentence Execution Summary

在当前阶段，更具体的执行策略可以概括为：

> 先以尽量少改源码的方式跑通 `RotatE/TransE + FB15k-237` 的 multiplicity 主实验，再基于稳定的评估链路推进 relation-level 分析与论文写作。
