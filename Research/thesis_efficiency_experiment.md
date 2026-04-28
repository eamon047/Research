# Efficiency / Reduced Computation Experiment

## Status

This note records an optional side branch for the thesis:

> resource-efficient voting approximation under a shared model-pool setting.

This branch is not required for closing the main relation-level structural
analysis. It should only be kept in the thesis if a small pilot produces a
simple and defensible efficiency result.

## Relation To The Main Thesis Block

The main thesis block asks:

> Which relation-level factors are associated with predictive multiplicity?

The efficiency branch asks a different question:

> If voting is used to mitigate predictive multiplicity, can a smaller shared
> model pool recover most of the mitigation effect obtained by a larger voting
> setup?

Therefore, this branch should not be presented as another relation-pattern
experiment. Its role is methodological and practical:

- the main block analyzes where multiplicity appears
- this branch asks whether an existing mitigation strategy can be made cheaper

If this connection cannot be explained briefly in writing or slides, the branch
should stay out of the main presentation.

## Prior Work Context

The original multiplicity release evaluates voting-based mitigation by creating
multiple outputs from trained KGE models.

In the local release code, the relevant parameters are:

- `num = 10`
- `agg_num = 8`
- `k = 10`

Operationally, this produces ten evaluated outputs. Under voting baselines, each
output is a community of `agg_num` models. Under the `without` baseline, the
same community index list is used, but only the baseline model in each community
contributes to scoring.

This branch should not claim to be a strict reproduction of the original voting
protocol. It is a local, resource-aware variant.

## Research Question

Recommended thesis-safe question:

> In a shared model-pool setting, can smaller voting communities recover most of
> the multiplicity reduction achieved by a larger voting setup while using fewer
> uniquely trained models?

This wording is intentionally narrower than:

> We reproduce the original voting protocol with fewer models.

The narrower wording is safer because shared pools create overlapping
communities, and that overlap changes the interpretation of output diversity.

## Proposed Design

For each model family and dataset:

1. choose a pool of `P` unique trained checkpoints
2. sample `C = 10` voting communities from that pool
3. each community contains `m` models
4. evaluate `without`, `major`, `borda`, and `range`
5. repeat community sampling over several random seeds

The current first target should be:

- model: `RotatE`
- dataset: `FB15k-237`
- local experiment directory: `LibKGE/local/RotatE_FB15k237`

Reason:

- the current local `RotatE` pool has more available seeds than `TransE`
- this makes it suitable for testing `P = 10 / 20 / 30` without new training

## Pilot Grid

Suggested first pilot:

| Variable | Values |
|---|---|
| `P` | `10, 20, 30` |
| `C` | `10` |
| `m` | `2, 3, 4, 5, 6, 8` |
| `k` | `10` |
| sampling seeds | `0, 1, 2, 3, 4` initially |
| voting methods | `major`, `borda`, `range` |

If runtime is acceptable and the trend is promising, increase sampling seeds
from `5` to `10`.

Do not train new checkpoints for `P = 40` until the `P <= 30` pilot shows that
the branch is worth expanding.

## Metrics To Report

For each setting, record:

- `model`
- `dataset`
- `pool_size` (`P`)
- `num_communities` (`C`)
- `community_size` (`m`)
- `sampling_seed`
- `baseline`
- `Hits`
- `Epsilon`
- `Alpha`
- `Delta`
- `unique_model_count`
- `total_voting_slots = C * m`
- `avg_pairwise_overlap`
- `avg_pairwise_jaccard`

Derived quantities:

- `alpha_reduction = (alpha_without - alpha_voting) / alpha_without`
- `delta_reduction = (delta_without - delta_voting) / delta_without`
- `alpha_recovery_vs_reference`
- `delta_recovery_vs_reference`

Where the larger voting reference should initially be:

- same `P`
- same `C`
- `m = 8`

This avoids comparing a reduced setting against a reference drawn from a
different model pool unless that comparison is explicitly intended.

## Main Caveat

In a shared-pool design, voting communities can overlap. If two communities use
many of the same models, their outputs may be more similar even before voting is
considered.

Therefore, a reduction in `Alpha` or `Delta` may come from both:

- aggregation inside each voting community
- lower diversity between the evaluated communities due to overlap

This caveat does not invalidate the branch, because the branch is about
resource-efficient approximation. But it must be measured and reported.

At minimum, report average pairwise community overlap and Jaccard similarity for
each setting.

## Interpretation Policy

A thesis-safe positive result would be:

> A shared pool of 20-30 models with smaller voting communities recovers most of
> the voting-based multiplicity reduction of a larger voting setup, suggesting
> that mitigation may not require fully independent large communities.

Avoid stronger claims such as:

- voting can always be reproduced with fewer models
- the proposed protocol is equivalent to the original paper's protocol
- reduced multiplicity is caused only by voting aggregation

## Decision Rule

After the first pilot:

- keep in the main thesis only if the result is simple, stable, and easy to
  explain
- move to appendix if the result is technically useful but secondary
- drop from the thesis if the result requires too many caveats or distracts from
  the relation-level main block

## Immediate Implementation Tasks

Before running the pilot:

1. add a small sweep script under `Multiplicity_rewrite/`
2. reuse the existing rank and voting utilities where possible
3. add explicit community-overlap statistics
4. write outputs under a separate results directory, for example:
   `results/RotatE_FB15k237/efficiency_voting/`
5. keep this branch separate from the existing relation-pattern result folders

Do not modify the closed relation-level main-line outputs for this branch.
