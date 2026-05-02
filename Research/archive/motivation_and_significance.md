# Predictive Multiplicity 的研究意义整理

## 1. 问题的核心困惑

在讨论 predictive multiplicity 时，一个很自然的疑问是：

> 如果一个模型的整体准确率是 80%，那么对于任意一个具体 query，我们是否可以认为它大约有 80% 的概率是正确的？  
> 如果是这样，那么 multiplicity 高或者低到底有什么影响？为什么还需要研究它？

这个问题非常关键，因为它关系到 predictive multiplicity 这个课题是否真的有意义。

简单说，问题的核心在于：

> **整体准确率是 80%，并不等价于每一个具体 query 都有 80% 的可靠性。**

整体准确率描述的是全局平均表现，而 predictive multiplicity 关注的是局部决策是否稳定。二者回答的是不同问题。

---

## 2. Global accuracy 和 query-level reliability 不是同一个概念

Hits@10 或 accuracy 这样的指标告诉我们：

> 在所有测试 query 中，平均有多少比例被模型正确处理。

但是它没有告诉我们：

> 对于某一个具体 query，不同性能相近的模型是否会给出一致的 top-K hit / miss 判断。

这两者之间存在重要差别。

假设有 10 个 query，一个模型 family 的整体 Hits@10 是 80%。这可能对应两种完全不同的情况。

### 情况 A：错误集合稳定

```text
Run 1: q1 q2 q3 q4 q5 q6 q7 q8 hit, q9 q10 miss
Run 2: q1 q2 q3 q4 q5 q6 q7 q8 hit, q9 q10 miss
Run 3: q1 q2 q3 q4 q5 q6 q7 q8 hit, q9 q10 miss
```

在这种情况下，模型虽然有 20% 的错误，但错误集中在稳定的一批 query 上。不同 repeated runs 之间的 hit / miss 判断基本一致。

这意味着模型的行为虽然不完美，但相对稳定。它稳定地解决某些 query，也稳定地无法解决另一些 query。

这种情况对应的是 **low predictive multiplicity**。

### 情况 B：错误集合不稳定

```text
Run 1: q1 q2 q3 q4 q5 q6 q7 q8 hit, q9 q10 miss
Run 2: q1 q2 q3 q4 q5 q6 q9 q10 hit, q7 q8 miss
Run 3: q1 q2 q3 q7 q8 q9 q10 hit, q4 q5 q6 miss
```

在这种情况下，不同 repeated runs 的整体 Hits@10 可能仍然接近 80%，但具体做对和做错的 query 并不一致。

也就是说：

> 模型整体表现看起来差不多，但具体到某一个 query，hit / miss decision 可能会随着 random seed 或训练扰动而变化。

这种情况对应的是 **high predictive multiplicity**。

这说明，global accuracy 相同，并不代表 query-level decision 的稳定性相同。

---

## 3. Predictive multiplicity 不是在问“模型平均准不准”

Predictive multiplicity 关注的不是模型平均准确率本身，而是：

> **在整体性能相近的模型之间，具体 query 的 top-K decision 是否稳定。**

换句话说，accuracy 问的是：

> 这个模型平均有多少 query 做对了？

而 multiplicity 进一步问的是：

> 这些做对和做错的 query，是不是稳定的一批？

这就是它和普通 performance metric 的区别。

如果两个模型 family 都有 80% Hits@10：

- 一个 family 的错误集合非常稳定；
- 另一个 family 的错误集合随着 random seed 大幅变化；

那么它们在 global accuracy 上可能一样，但在 reliability 上并不一样。

---

## 4. 对一个具体 query 来说，multiplicity 的影响是什么？

对于一个具体 query，真正需要关心的不只是：

> 这个模型整体 accuracy 是多少？

还应该关心：

> 对这个 query，不同性能相近的模型是否给出一致的 hit / miss 判断？

如果多个 similarly performing models 对同一个 query 都给出 hit，那么我们可以认为这个 query 的预测相对稳定。这说明模型可能从训练图中学到了比较一致的 relational evidence。

相反，如果多个 similarly performing models 对同一个 query 的判断一半是 hit、一半是 miss，那么即使它们整体 Hits@10 都很高，这个 query 的预测仍然应该被视为不稳定。

这种不稳定可能意味着：

- 该 query 位于模型 ranking decision 的边界附近；
- 训练图中支持该 query 的 evidence 不够稳定；
- 模型对该 relation structure 的学习存在不确定性；
- 最终结果可能受到 random seed 或训练过程扰动的影响。

因此，multiplicity 提供的是一种 **local reliability signal**。

它不是替代 accuracy，而是补充 accuracy。

可以这样理解：

> Accuracy tells us how well the model performs on average.  
> Multiplicity tells us whether individual decisions are stable across similarly performing models.

---

## 5. 为什么这个问题在 KGE link prediction 中尤其重要？

KGE link prediction 通常不是简单的二分类任务，而是 ranking 任务。

例如：

```text
(Paris, capital_of, ?)
```

模型需要对所有候选 tail entities 进行打分并排序。如果正确答案排在前 K 名以内，就是 hit；否则就是 miss。

在这种设定下，两个整体 Hits@10 相近的模型可能对同一个 query 给出完全不同的结果：

- Model A 把正确答案排在第 5 名，因此是 hit；
- Model B 把正确答案排在第 20 名，因此是 miss。

从 global accuracy 看，这两个模型可能差不多。但从这个具体 query 的角度看，它们的结论完全不同。

如果 KGE prediction 被用于下游任务，比如：

- 知识库补全；
- 推荐候选实体；
- 辅助关系判断；
- 给下游推理系统提供 evidence；

那么这种 query-level instability 就可能产生实际风险。

因为这意味着：

> 最终结论可能不是由 graph 中稳定的 relational evidence 决定的，而是由 random seed、初始化或训练过程中的偶然扰动决定的。

这就是 predictive multiplicity 的问题意识。

---

## 6. “80% accuracy” 为什么不能直接理解为“每个 query 有 80% 概率正确”

从经验角度说，如果我们完全不知道 query 的任何信息，那么整体 accuracy 可以作为一个非常粗略的平均先验。

但是，这个先验不能说明每个 query 的真实可靠性。

原因是 query 之间并不是同质的。不同 query 可能具有不同难度：

- 有些 query 结构非常明确，几乎所有模型都能稳定预测正确；
- 有些 query 本身很困难，几乎所有模型都预测错误；
- 有些 query 位于决策边界附近，不同 repeated runs 之间容易出现 hit / miss 冲突。

整体 accuracy 把这些 query 全部平均在一起，因此会掩盖 query-level 的差异。

所以，“整体准确率 80%”更准确的理解是：

> 在测试集整体分布上，模型平均有 80% 的 query 是 hit。

而不是：

> 对于每一个具体 query，模型都有同样的 80% 可靠性。

Predictive multiplicity 正是在试图揭示这种被 global metric 掩盖的局部不稳定性。

---

## 7. Multiplicity 高和低分别意味着什么？

### Low multiplicity

Low multiplicity 表示：

> 不同性能相近的模型在 query-level 上给出的 hit / miss 判断比较一致。

这意味着模型行为相对稳定。即使模型会犯错，它也可能是在相同类型、相同 query 上稳定犯错。

这种情况下，我们可以更清楚地知道：

- 哪些 query 是模型稳定能解决的；
- 哪些 query 是模型稳定不能解决的。

### High multiplicity

High multiplicity 表示：

> 不同性能相近的模型在许多 query 上给出的 hit / miss 判断不一致。

这意味着：

- 模型整体表现可能不错；
- 但具体 query 的 decision 不稳定；
- 某些 prediction 可能依赖训练随机性；
- 单个模型输出的可信度需要被谨慎对待。

所以 high multiplicity 并不是简单地说“模型准确率低”，而是说：

> 模型的 query-level decision 缺乏稳定性。

这是一种和 accuracy 不同的风险。

---

## 8. 我的研究为什么有意义？

如果只是证明 KGE 中存在 predictive multiplicity，那么意义可能有限，因为原论文已经做了这件事。

真正有价值的研究问题应该是：

> Predictive multiplicity 是否在不同 relation 上均匀发生？  
> 还是说，它会在某些 relation-level structure 上更加明显？

这就是 relation-level analysis 的意义。

你的研究不是单纯重复原论文的结论，而是把问题从：

> multiplicity 是否存在？

推进到：

> multiplicity 在哪里更严重？  
> 它是否和 relation-level factors 有系统关系？

这就形成了更明确的 thesis contribution。

---

## 9. Relation-level analysis 的核心价值

在你的当前实验中，最重要的观察是 mapping type 的影响。

例如在 tail prediction 中：

- 1-N relation 往往表现出更高的 multiplicity；
- M-1 relation 往往更加稳定；
- 当 prediction side 从 tail 换成 head 后，模式出现方向性的镜像变化。

这说明 predictive multiplicity 并不是完全随机的噪声。它和 relation 的结构形态有关，尤其和 prediction side 上是 one-side 还是 many-side 有关。

因此，你的研究可以被理解为：

> 不是简单地说 KGE 模型有时不稳定，  
> 而是进一步指出这种不稳定性集中出现在哪些 relation structure 中。

这比单纯讨论 global multiplicity 更有解释力。

---

## 10. 可以如何概括这个研究的意义

可以用三句话总结：

### 1. Global accuracy hides local instability.

整体 Hits@10 只能说明平均性能，不能说明每个 query 的 decision 是否稳定。

### 2. Predictive multiplicity identifies query-level disagreement among similarly performing models.

Predictive multiplicity 衡量的是：整体性能相近的模型之间，是否会对同一个 query 给出不同的 hit / miss 判断。

### 3. Relation-level analysis explains where this instability is concentrated.

Relation-level analysis 进一步追问：这种不稳定性是否和 relation structure 有关，以及哪些 relation-level factors 更容易导致 multiplicity。

---

## 11. 汇报中可以使用的研究动机表达

英文版本：

> Hits@10 tells us how well a model performs on average, but it does not tell us whether the same individual queries are consistently solved across similarly performing models.  
> Predictive multiplicity fills this gap by measuring query-level instability among models with comparable global performance.  
> My thesis further asks whether this instability is randomly distributed, or whether it is systematically associated with relation-level structure.

中文理解：

> Hits@10 告诉我们模型平均表现如何，但它不告诉我们：具体哪些 query 是稳定被解决的。  
> Predictive multiplicity 补充了这个视角，它衡量的是整体性能相近的模型之间，在 query-level 上是否会发生 hit / miss 冲突。  
> 我的研究进一步追问的是：这种不稳定性是不是随机分布的，还是和 relation-level structure 有系统关系。

---

## 12. 最终核心观点

Predictive multiplicity 的意义不在于替代 accuracy，而在于指出 accuracy 之外的另一个问题：

> 一个模型 family 即使整体表现很好，也可能在具体 query 上表现出不稳定的 decision behavior。

而 relation-level multiplicity analysis 的意义在于进一步解释：

> 这种不稳定性不是均匀分布的，而是可能和 relation structure 系统相关。

因此，这个研究的核心价值可以概括为：

> 从 global performance 走向 local reliability，  
> 再从 local instability 走向 relation-level structural explanation。
