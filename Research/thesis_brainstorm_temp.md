# Symmetry Family：数理定义与实验设计整理

## 1. 背景与定位

本文当前主线问题是：

> 不同 relation pattern 下，KGE 的 predictive multiplicity 是否存在系统性差异？

在这个框架下，`symmetry` 与 `mapping type` 一样，都是**单个 relation 的结构属性**。  
这与 `inverse family` 不同：inverse 天然涉及两个 relation 的配对关系，而 symmetry 只涉及同一个 relation 内部的双向支持。

因此，symmetry 这一节非常适合继续沿用当前 thesis 的主分析单位：

- 数据集：`FB15k-237`
- 模型设定：同一 KGE 模型 repeated runs
- 分析层级：`relation-level`

也就是说，这一节最终仍然保持：

> 每个 relation 一行，再分析其 symmetry 特征与 relation-level multiplicity 指标之间的关系。

---

## 2. 研究目标

symmetry family 这一部分最稳妥的研究目标不是证明“哪些 relation 是对称关系”，而是研究：

> 一个 relation 的对称性强弱，是否与该 relation 上的 predictive multiplicity severity 有关？

更具体地说，可以拆成三个问题：

1. 某 relation 的 symmetry score 是否与 `alpha_r` 有关？
2. 某 relation 的 symmetry score 是否与 `delta_r` 有关？
3. 某 relation 的 symmetry score 是否与 `hits_r` 有关？

其中：

- `alpha_r` 和 `delta_r` 是主分析目标
- `hits_r` 是辅助结果，不应喧宾夺主

---

## 3. 为什么 symmetry 比 inverse 更直观？

因为 symmetry 是 relation 自己的属性。

如果 relation `r` 具有较强对称性，那么在训练图中：

- `(h, r, t)` 出现时
- `(t, r, h)` 也往往出现

它不需要：

- 第二个 relation
- best partner
- mutual score
- clarity score

因此 symmetry family 可以直接在 relation-level 上定义，不需要像 inverse 那样先 pair-level 再压缩成 relation-level proxy。

---

## 4. 数理定义

### 4.1 训练图与关系边集

记训练图为：

```math
\mathcal{G}_{train} \subseteq \mathcal{E} \times \mathcal{R} \times \mathcal{E}
```

其中：

- `\mathcal{E}` 是实体集合
- `\mathcal{R}` 是关系集合

对任意 relation `r \in \mathcal{R}`，定义其边集合为：

```math
E_r = \{(h,t) \mid (h,r,t) \in \mathcal{G}_{train}\}
```

它表示：

> relation `r` 在训练图中连接的所有有向实体对。

---

### 4.2 Symmetric-Pair Set

对于 relation `r`，定义其对称支持子集为：

```math
E_r^{sym} = \{(h,t) \in E_r \mid (t,h) \in E_r\}
```

其含义是：

> 在 relation `r` 的所有事实中，那些能够在同一 relation 下找到反向事实支持的边。

换句话说，如果：

- `(h,r,t)` 在训练图中存在
- 且 `(t,r,h)` 也在训练图中存在

那么 `(h,t)` 会被计入 `E_r^{sym}`。

---

### 4.3 Relation-Level Symmetry Score

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

- `0`：完全没有观察到对称支持
- `1`：所有边都能找到反向对应，表现为完全对称
- 中间值：部分对称

---

## 5. 直观例子

### 5.1 高 symmetry 的典型关系

例如关系 `sibling_of`：

- `(Alice, sibling_of, Bob)`
- `(Bob, sibling_of, Alice)`

通常会成对出现，因此 symmetry score 会较高。

### 5.2 低 symmetry 的典型关系

例如关系 `parent_of`：

- `(Alice, parent_of, Bob)`

通常不会伴随：

- `(Bob, parent_of, Alice)`

因此 symmetry score 会很低。

---

## 6. 是否需要单独定义 antisymmetry？

当前阶段，不建议一开始就为 antisymmetry 再单独构造一整套复杂定义。

原因有三点：

1. 在真实 KG 中，很多 relation 不是严格数学意义上的反对称，只是“低对称”
2. thesis 当前主线更适合先用连续分数做 relation-level 统计
3. 低 `symmetry_score` 本身已经能覆盖大多数“非对称 / 近似反对称”关系

因此，第一版建议：

- 主分析变量：`symmetry_score`
- 不急着额外定义严格的 `antisymmetry_score`

如果后面结果很有信号，再考虑补一个辅助定义，例如：

```math
\operatorname{AntiSymProxy}(r)=1-\operatorname{Sym}(r)
```

但这更适合作为解释性辅助量，而不是当前主分析核心。

---

## 7. 核心假设

### H1：结构性关联假设

**relation 的 symmetry score 与 predictive multiplicity severity 存在关联。**

更具体地说，可以提出一个较温和的直觉：

> 对称性更强的 relation 可能在训练图中具有更强的内部双向结构支持，因此 repeated runs 之间更容易得到一致预测，从而 relation-level multiplicity 可能更低。

这里的表述应保持为：

- 结构关联
- 不宜过早写成强因果律

### H2：模型交互假设（可选扩展）

如果后面补多个模型，可以进一步研究：

> symmetry 的影响是否依赖于模型家族？

例如：

- 某些模型对高 symmetry relation 更稳定
- 某些模型对低 symmetry relation 更脆弱

但如果当前仍以 `RotatE` 为主，H2 可以先不展开。

---

## 8. 与 multiplicity 指标的对接方式

symmetry family 不需要重新定义 multiplicity 指标。  
应直接沿用 thesis 当前 relation-level multiplicity 表中的结果变量。

推荐至少保留：

- `hits_r`
- `alpha_r`
- `delta_r`
- `test_support`

如果已经有更细的支持变量，也可以一并保留：

- `eligible_support`
- `head_support`
- `tail_support`

但对于 symmetry 第一轮分析，不是必须。

---

## 9. 最终 relation-level 表结构

完成 symmetry 统计并与 multiplicity 表 merge 之后，推荐的 relation-level 主分析表至少包含：

- `relation_id`
- `relation_name`
- `train_support`
- `symmetry_score`
- `test_support`
- `hits_r`
- `alpha_r`
- `delta_r`

如果要和其他 pattern 联动，也可以保留：

- `mapping_type`
- `answer_cardinality`
- `frequency`

但 symmetry 第一轮不必强求一开始就全部并入。

---

## 10. 实验实施方式

### Step 1：仅使用训练集计算 symmetry score

这一点很重要：

> symmetry 作为 relation pattern，只能使用训练图来定义。

不要用验证集或测试集的三元组来定义 relation 的 symmetry 特征，以避免特征定义时使用测试信息。

因此：

- `E_r`
- `E_r^{sym}`
- `Sym(r)`

全部只从训练图构建。

---

### Step 2：为每个 relation 计算 symmetry score

实现流程建议为：

1. 读入训练集三元组
2. 为每个 relation 构建 `E_r`
3. 对每个 relation：
   - 遍历其边 `(h,t)`
   - 检查 `(t,h)` 是否也在 `E_r`
4. 统计：
   - `train_support = |E_r|`
   - `symmetric_pair_count = |E_r^{sym}|`
   - `symmetry_score = |E_r^{sym}| / |E_r|`

### 输出文件建议

例如输出为：

`relation_symmetry_stats.csv`

包含字段：

- `relation_id`
- `relation_name`
- `train_support`
- `symmetric_pair_count`
- `symmetry_score`

---

### Step 3：与 relation-level multiplicity 表做 merge

将 `relation_symmetry_stats.csv` 与你当前已有的 relation-level multiplicity 结果表按 relation 连接。

例如 merge 后得到：

`relation_symmetry_multiplicity_merged.csv`

包含：

- `relation_id`
- `relation_name`
- `symmetry_score`
- `hits_r`
- `alpha_r`
- `delta_r`
- `test_support`

---

### Step 4：进行基础统计分析

symmetry 第一轮分析建议保持简单、可解释。

#### 4.1 相关性分析

优先计算 Spearman correlation：

- `symmetry_score` vs `alpha_r`
- `symmetry_score` vs `delta_r`
- `symmetry_score` vs `hits_r`

推荐原因：

- symmetry score 很可能分布偏斜
- relation-level 指标通常也不一定满足线性关系
- Spearman 更稳妥

---

#### 4.2 分桶分析

将 `symmetry_score` 分桶，例如：

- `0`
- `(0, 0.2]`
- `(0.2, 0.5]`
- `(0.5, 1.0]`

或者按分位数分桶：

- low
- medium
- high

然后比较每个桶的平均：

- `mean hits_r`
- `mean alpha_r`
- `mean delta_r`

这一步通常比单纯的散点图更适合 thesis 叙事。

---

## 11. 推荐图表

### 必做图

#### 图 1：Symmetry Score vs Alpha

- 横坐标：`symmetry_score`
- 纵坐标：`alpha_r`
- 图形：散点图 + 趋势线

#### 图 2：Symmetry Score vs Delta

- 横坐标：`symmetry_score`
- 纵坐标：`delta_r`
- 图形：散点图 + 趋势线

---

### 推荐图

#### 图 3：Symmetry Score vs Hits@10

- 横坐标：`symmetry_score`
- 纵坐标：`hits_r`
- 图形：散点图 + 趋势线

#### 图 4：Bucket-based Mean Plot

- 横坐标：symmetry-score 分桶
- 纵坐标：平均指标值
- 可分别画：
  - `mean alpha_r`
  - `mean delta_r`
  - `mean hits_r`

---

## 12. 推荐的 sanity check

在正式做 multiplicity 分析之前，建议先检查 symmetry-score 的分布是否“可用”。

需要至少确认：

1. 是否大量 relation 的 symmetry score 都为 0
2. 是否存在一个非空的高 symmetry subgroup
3. 分布是否有足够 spread，支持后续分桶分析
4. 高 symmetry relations 在语义上是否看起来合理

这一步很重要，因为即使定义在数学上成立，如果分布几乎退化为全零，也很难支撑 thesis 分析。

---

## 13. 推荐的控制变量分析

如果 symmetry 第一轮结果看起来有信号，第二轮建议优先控制 `mapping_type`。

原因：

- `mapping_type` 已经是你 thesis 主结果
- symmetry 很可能并不独立于 mapping structure
- 某些 mapping type 本身就更可能出现高 / 低 symmetry

因此，最自然的 follow-up 是：

### 分层分析
在每个 `mapping_type` 内，再分析：

- `symmetry_score` vs `alpha_r`
- `symmetry_score` vs `delta_r`

### 或回归分析
例如：

```math
\text{severity}(r) \sim \operatorname{Sym}(r) + \text{MappingType}(r)
```

如果要更简单一点，也可以先只做 bucket comparison within mapping type。

---

## 14. Case Study 建议

建议在正式写作时补一小段 case study。

### 高 symmetry relation
挑若干 symmetry score 很高的 relation，检查：

- 它们是否语义上确实接近对称
- 它们是否更稳定
- 它们是否更容易预测

### 低 symmetry relation
挑若干 symmetry score 很低的 relation，检查：

- 它们是否语义上本就不应对称
- 它们是否更容易出现 multiplicity
- 如果没有，也能说明 symmetry 不是唯一因素

这类案例有助于防止结果只剩“统计相关但没有解释”。

---

## 15. 论文里可直接使用的表述

### 中文版

本文将 symmetry family 视为 relation 自身的单关系结构属性。具体而言，我们在训练图上定义每个 relation 的 symmetry score，用于衡量该 relation 的事实中有多大比例能够在同一 relation 下找到反向事实支持。该 symmetry score 被作为 relation-level 的结构特征，与 predictive multiplicity 的关系层级指标（如 `alpha_r`、`delta_r` 和 `hits_r`）进行关联分析。

### 英文版

We treat the symmetry family as a single-relation structural property. Specifically, for each relation, we define a symmetry score on the training graph, measuring the proportion of facts whose reversed counterparts also appear under the same relation. This relation-level symmetry score is then analyzed against relation-level predictive multiplicity metrics, such as `alpha_r`, `delta_r`, and `hits_r`.

---

## 16. 当前最小可运行版本（推荐优先实现）

如果当前目标是尽快得到第一轮结果，建议先只做下面三步：

1. 计算每个 relation 的 `symmetry_score`
2. 与现有 relation-level multiplicity 表 merge
3. 输出两张图：
   - `symmetry_score vs alpha_r`
   - `symmetry_score vs delta_r`

只要这三步跑通，symmetry section 就已经具备雏形。

之后再视结果决定是否补：

- `hits_r`
- 分桶分析
- mapping-type interaction
- case study

---

## 17. 一句话总结

Symmetry family 这一节的核心不是研究“哪些关系在语义上是 textbook symmetric relation”，而是研究：

> **一个 relation 在训练图中表现出的内部双向支持强度，是否与其在 repeated runs 下的 predictive multiplicity severity 有关。**
