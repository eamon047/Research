# Short English Script for 5.8 Zemi

## Slide 1

Today I will present my current research progress.
The topic is relation-level structural analysis of predictive multiplicity in knowledge graph embedding link prediction.
The main goal is to understand whether predictive multiplicity is only a global model-level phenomenon, or whether it is systematically related to relation-level structure.

## Slide 2

Before introducing predictive multiplicity, I will briefly explain the basic task of KGE link prediction.
A knowledge graph represents facts as triples, consisting of a head entity, a relation, and a tail entity.
In link prediction, the input is an incomplete query, such as `(h, r, ?)` or `(?, r, t)`.

KGE models learn embeddings for entities and relations, score candidate triples, and rank all candidate entities.
For example, for `(Paris, capital_of, ?)`, the model ranks candidate tail entities.
If the correct answer appears in the top 10, the query is counted as a Hit@10; otherwise, it is a Miss@10.
Hits@10 is the proportion of test queries satisfying this top-10 condition.

This top-10 hit or miss decision is important because predictive multiplicity asks whether the same query receives stable top-10 decisions across repeated runs.

## Slide 3

Now we can ask a more specific question:
if we train the same KGE model family multiple times with different random seeds, do these models always give the same top-K hit or miss decision for the same query?

Predictive multiplicity refers to this query-level instability.
Even when repeated runs have very similar overall performance, they may still disagree on individual queries.
The key point is that similar overall Hits@10 does not imply identical query-level decisions.

The toy example shows this clearly.
All three models have the same overall Hits@10, which is 75%.
However, the first three queries receive conflicting hit or miss decisions across models, while only the fourth query is stable.

The original paper uses two metrics to quantify this.
Ambiguity, or alpha, asks how many queries receive at least one conflicting top-K decision.
Here, three out of four queries are unstable, so alpha is 0.75.

Discrepancy, or delta, measures the largest disagreement rate between the baseline model and a competing model.
Using Model A as the baseline, both Model B and Model C disagree with it on two out of four queries, so delta is 0.5.

So, alpha measures how widespread instability is across queries, while delta measures how strongly one competing model can disagree with the baseline.
This motivates my thesis question: where does this instability become stronger?

## Slide 4

The original paper mainly establishes the existence of predictive multiplicity in KGE link prediction.
It formalizes the phenomenon, introduces ambiguity and discrepancy, and shows that voting can reduce multiplicity to some extent.

My thesis starts from a different question.
Instead of only asking whether predictive multiplicity exists globally, I ask whether it behaves differently across relations.
In other words, I shift the focus from a global model-level phenomenon to relation-level analysis.

The main question is:
which relation-level factors are associated with stronger or weaker predictive multiplicity?

## Slide 5

This slide summarizes the thesis setting and analysis pipeline.
The current study uses FB15k-237 and focuses on two representative KGE models: RotatE and TransE.
FB15k-237 reduces inverse-relation leakage compared with the original FB15k, so it is suitable for structural analysis in link prediction.

I train the same model family multiple times with different random seeds.
The goal here is to analyze raw predictive multiplicity before applying any voting method.

The analysis unit is relation-level.
For each relation, I compute Hits@10, alpha, and delta from query-level top-10 outcomes.
Then I attach relation-level factors, such as mapping property, inverse-like support, symmetry, and relation frequency.
Finally, I compare which factors are associated with stronger multiplicity.

So the current goal is diagnosis, not mitigation.
I want to identify where multiplicity becomes more serious, and which relation structures deserve attention.

## Slide 6

This slide introduces the candidate relation-level factors.
The selection principle is that predictive multiplicity is a top-K ranking instability.
So I focus on factors that may affect answer-space ambiguity, structural support, or data sparsity.

The first factor is mapping property.
It describes how many heads and tails are typically associated with a relation, using categories such as 1-to-1, 1-to-N, M-to-1, and M-to-N.
This factor is important because it changes the number of plausible candidates on the prediction side.
When the prediction target is on the many-side, the top-K boundary may become less stable.

The second factor is inverse-like support.
It asks whether a relation has a clear reverse partner, such as `parent_of` and `child_of`.
If reverse-side evidence supports the same entity pair, the model may learn more consistent ranking behavior.

The third factor is symmetry.
This is different from inverse-like support because it looks at bidirectional support inside the same relation, such as `married_to` or `adjacent_to`.

The fourth factor is relation frequency.
I use it mainly as a support and sparsity control, to check whether observed structural effects are really due to relation structure, rather than simply data scarcity.

## Slide 7

Now I move to the main result: mapping property.
This slide shows RotatE on tail prediction, where the query form is `(h, r, ?)`.

The left plot shows Hits@10, and the middle and right plots show alpha and delta.
Higher alpha and delta mean stronger instability across repeated runs.

The key message is that tail-side multiplicity follows the answer-space structure of the relation.
For 1-to-N relations, the tail side is the many-side.
For the same `(h, r)`, there may be many plausible tail candidates, so the top-K boundary is harder to stabilize.
This is why 1-to-N shows low Hits@10 and high alpha and delta.

In contrast, M-to-1 is more constrained on the tail side.
The answer space is more concentrated, so different runs are more likely to make consistent top-K decisions.
As a result, M-to-1 has higher Hits@10 and lower multiplicity.

M-to-N is also tail-many, but it is less extreme.
It may combine a larger candidate space with broader many-to-many structural redundancy, so it behaves as an intermediate case.

The main takeaway is that predictive multiplicity is not merely random seed noise.
It is systematically related to relation-level answer-space structure.

## Slide 8

This slide checks whether the mapping-property result is robust and directional.

The first check is cross-model consistency.
Here, I switch from RotatE to TransE, while still using tail prediction.
The same tail-side contrast remains visible:
M-to-1 remains the most stable regime, while 1-to-N remains the most multiplicity-prone regime.
This suggests that the pattern is not specific to RotatE.

The second check is the prediction-side check.
Here, I return to RotatE, but switch from tail prediction to head prediction.
Now the pattern reverses:
1-to-N becomes stable, while M-to-1 becomes multiplicity-prone.

This reversal is important.
It shows that multiplicity follows the predicted side, not a fixed mapping-type label.
When the prediction target is on the many-side, the answer space becomes more dispersed, and the top-K boundary becomes less stable.

So mapping property gives the strongest and most directional relation-level signal in the current analysis.

## Slide 9

The second result is inverse-like support.
Unlike mapping property, inverse-like support does not show a clean global trend.
However, it becomes informative for high-confidence inverse-like relations.

I use two metrics.
The first is mutual inverse strength.
It measures whether two relations provide reverse support for each other in the training graph.
The second is inverse clarity.
It measures whether the best reverse partner is clearly better than other candidate reverse relations.

The table shows that high-confidence inverse-like subgroups have higher Hits@10 and lower alpha and delta than the overall reference.
The clearest case is the subgroup with inverse clarity greater than 0.5.
For this subgroup, both RotatE and TransE reach alpha = 0 and delta = 0.

My interpretation is that a clear reverse partner provides a strong reverse-side structural constraint.
For an entity pair, the graph can support both `(h, r, t)` and `(t, r_inv, h)`.
This makes it easier for repeated runs to learn consistent ranking behavior.

The education relation pair at the bottom is an intuitive example.
One relation means the institution of a campus, and the other means the campuses of an institution.
This pair is semantically clear, has high mutual inverse strength and clarity, and shows completely stable prediction results.

So inverse-like support is not a global explanatory factor, but it can identify a small group of locally stable high-confidence inverse-like relations.

## Slide 10

The third result is symmetry.
Here, the conclusion is weaker:
symmetry alone does not define a stable regime.

First, the global Spearman correlations are close to zero for both RotatE and TransE.
This means that symmetry score is not strongly associated with Hits@10, alpha, or delta at the global relation level.

Second, the bucket comparison is non-monotonic.
If symmetry were a strong stability factor, we might expect higher symmetry to lead to lower multiplicity.
But this is not what we observe.
Weak nonzero symmetry has lower Hits@10 and higher multiplicity, while high symmetry recovers Hits@10 but does not form a clearly low-multiplicity regime.

My interpretation is that symmetry provides only a coarse type-level constraint.
For example, symmetric relations may connect entities of similar semantic types.
This can help rough filtering, but it does not necessarily identify the correct entity for a specific query.
If many candidates have similar types, competition near the top-K boundary can still be strong.

Therefore, symmetry is a reasonable candidate factor, but not a strong standalone explanatory factor in this setting.

## Slide 11

Finally, I summarize the current findings and future work.

The main conclusion is that predictive multiplicity shows relation-level structural heterogeneity.
It should not be analyzed only as a global model-level phenomenon.

Among the factors studied here, mapping property gives the strongest and most directional signal.
Multiplicity follows the predicted side of the relation:
when the prediction target is on the many-side, the answer space becomes less stable.

Inverse-like support works differently.
It is not a clean global factor, but high-confidence inverse-like pairs can form a locally stable subgroup.

Symmetry is weaker.
It may provide type-level constraints, but it does not define a clean stable regime by itself.

For future work, the first direction is relation frequency as a control factor.
I need to examine more strictly whether the mapping-property effect remains after controlling for relation support and sparsity.

The second direction is broader validation.
The current experiments focus on FB15k-237, RotatE, and TransE.
Future work should extend the analysis to more datasets and model families.

The third direction is from diagnosis to mitigation.
If relation-level signals can identify unstable regimes, they may help design targeted voting or adaptive ensemble strategies.

Overall, this work suggests that predictive multiplicity in KGE link prediction is not only a model-level issue.
It is also related to relation-level structural regimes.
