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

The original paper evaluates voting-based mitigation by constructing aggregated
outputs from trained KGE models. Conceptually, for each evaluated model, a
voting community is formed by training additional models with the same
configuration but different random seeds.

This local branch does not use the original paper's full independent voting
community protocol. Instead, it studies a smaller shared-pool variant:

- choose a limited pool of `P` unique trained checkpoints
- sample `C` voting communities from that shared pool
- vary the community size `m`
- measure how much of the within-grid larger-community effect is recovered

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

Where the local larger-community reference should initially be:

- same `P`
- same `C`
- `m = 8`

Here `m = 8` is not an original-paper baseline. It is simply the largest
community size in the current pilot grid, used to ask how much of the local
larger-community effect is recovered by `m = 2 / 4 / 6`.

This avoids comparing a reduced setting against a reference drawn from a
different model pool or a different protocol unless that comparison is
explicitly intended.

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

> Within a shared model-pool setting, smaller voting communities recover most of
> the reduction achieved by the largest community size in the pilot grid,
> suggesting that a cheaper local approximation may be possible.

Avoid stronger claims such as:

- voting can always be reproduced with fewer models
- the proposed protocol is equivalent to the original paper's protocol
- `m = 8` is the original-paper voting baseline
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

1. use `Multiplicity_rewrite/efficiency_voting_sweep.py`
2. reuse the existing rank and voting utilities where possible
3. keep explicit community-overlap statistics
4. write outputs under a separate results directory, for example:
   `results/RotatE_FB15k237/efficiency_voting/`
5. keep this branch separate from the existing relation-pattern result folders

Do not modify the closed relation-level main-line outputs for this branch.

Current implementation status:

- initial sweep script added: `Multiplicity_rewrite/efficiency_voting_sweep.py`
- script outputs global `Hits / Epsilon / Alpha / Delta` rows for each setting
- script records pool membership, community membership, unique model count,
  total voting slots, average pairwise overlap, and average pairwise Jaccard
- script computes reduction relative to `without` and recovery relative to the
  configured local larger-community reference
- script supports `--plan-only` to verify sweep settings and overlap statistics
  without loading checkpoints or running link-prediction evaluation
- initial pilot plan written to:
  `results/RotatE_FB15k237/efficiency_voting/sweep_plan.csv`

## Completed Pilot: `P = 10 / 20`

Status:

- completed for `RotatE + FB15k-237`
- pool sizes: `P = 10, 20`
- number of communities: `C = 10`
- community sizes: `m = 2, 4, 6, 8`
- sampling seeds: `0, 1, 2`
- baselines: `without`, `major`, `borda`, `range`

Output files:

- `results/RotatE_FB15k237/efficiency_voting/sweep_P10.csv`
- `results/RotatE_FB15k237/efficiency_voting/sweep_P10.log`
- `results/RotatE_FB15k237/efficiency_voting/sweep_P20.csv`
- `results/RotatE_FB15k237/efficiency_voting/sweep_P20.log`

Both CSV files contain the expected `48` result rows plus header:

> `1 pool size * 4 community sizes * 3 sampling seeds * 4 baselines = 48`

The logs end with successful `Saved sweep results` messages. The only observed
warnings are PyTorch sparse tensor deprecation warnings, which do not affect the
current interpretation.

### Main Numerical Summary

The table below reports means over sampling seeds `0, 1, 2`.

#### Range Voting

| `P` | `m` | `Alpha` | `Delta` | `alpha_reduction` | `delta_reduction` | `alpha_recovery_vs_m8` | `delta_recovery_vs_m8` | avg Jaccard |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 2 | 0.1660 | 0.0695 | 0.3039 | 0.2397 | 0.3800 | 0.3114 | 0.0988 |
| 10 | 4 | 0.1065 | 0.0495 | 0.5533 | 0.4587 | 0.6918 | 0.5957 | 0.2505 |
| 10 | 6 | 0.0748 | 0.0338 | 0.6863 | 0.6302 | 0.8581 | 0.8191 | 0.4357 |
| 10 | 8 | 0.0477 | 0.0211 | 0.7998 | 0.7697 | 1.0000 | 1.0000 | 0.6770 |
| 20 | 2 | 0.1723 | 0.0701 | 0.2785 | 0.2254 | 0.4177 | 0.3656 | 0.0568 |
| 20 | 4 | 0.1227 | 0.0514 | 0.4862 | 0.4317 | 0.7293 | 0.7000 | 0.1204 |
| 20 | 6 | 0.0977 | 0.0395 | 0.5906 | 0.5638 | 0.8859 | 0.9140 | 0.1817 |
| 20 | 8 | 0.0796 | 0.0347 | 0.6667 | 0.6169 | 1.0000 | 1.0000 | 0.2622 |

#### Borda Voting

| `P` | `m` | `Alpha` | `Delta` | `alpha_reduction` | `delta_reduction` | `alpha_recovery_vs_m8` | `delta_recovery_vs_m8` | avg Jaccard |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 2 | 0.1684 | 0.0709 | 0.2939 | 0.2252 | 0.3675 | 0.2935 | 0.0988 |
| 10 | 4 | 0.1074 | 0.0508 | 0.5495 | 0.4439 | 0.6871 | 0.5784 | 0.2505 |
| 10 | 6 | 0.0741 | 0.0340 | 0.6894 | 0.6287 | 0.8620 | 0.8201 | 0.4357 |
| 10 | 8 | 0.0477 | 0.0213 | 0.7999 | 0.7669 | 1.0000 | 1.0000 | 0.6770 |
| 20 | 2 | 0.1765 | 0.0714 | 0.2607 | 0.2103 | 0.3939 | 0.3419 | 0.0568 |
| 20 | 4 | 0.1246 | 0.0523 | 0.4779 | 0.4216 | 0.7219 | 0.6848 | 0.1204 |
| 20 | 6 | 0.0989 | 0.0405 | 0.5857 | 0.5527 | 0.8846 | 0.8979 | 0.1817 |
| 20 | 8 | 0.0807 | 0.0348 | 0.6621 | 0.6158 | 1.0000 | 1.0000 | 0.2622 |

### Initial Reading

The current pilot supports three observations:

1. `range` and `borda` show a clear monotonic pattern: larger voting communities
   reduce `Alpha` and `Delta` more strongly.
2. within this pilot grid, `m = 6` already recovers most of the local `m = 8`
   effect, especially for `P = 20`:
   - `range`: `alpha_recovery_vs_m8 = 0.8859`,
     `delta_recovery_vs_m8 = 0.9140`
   - `borda`: `alpha_recovery_vs_m8 = 0.8846`,
     `delta_recovery_vs_m8 = 0.8979`
3. `major` is not a good main mitigation baseline in this setting. It gives
   much lower `Hits` and can increase multiplicity for small `m`, so it should
   be kept only as a diagnostic comparison unless later results change this
   assessment.

Important caveat:

- `P = 10` sometimes shows stronger apparent reduction than `P = 20`, but its
  average community Jaccard is also much higher
- for example, with `m = 8`, average Jaccard is `0.6770` for `P = 10` but only
  `0.2622` for `P = 20`
- therefore, `P = 10` should not be interpreted as simply "better"; part of the
  reduction may come from stronger community overlap and lower output diversity

Current next step:

- run the same reduced pilot for `P = 30` using the existing `RotatE` model pool
- do not train additional checkpoints before inspecting whether `P = 30`
  materially changes the conclusion from `P = 20`
