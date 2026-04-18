# Thesis Symmetry Experiment

## Purpose of This Note

This note records the planned setup, implementation path, output structure, and interpretation rules for the symmetry-family analysis under the thesis main line.

Unlike `thesis_theory.md`, this file is not meant to freeze abstract definitions forever. It is a working experiment note for thesis writing and iteration.

At the current stage, this document should be treated as an experiment record that already includes both the `RotatE` baseline and the first `TransE` comparison run.

## Current Scope

The intended first-round symmetry study follows the same narrow thesis setup already used for the mapping-type and inverse sections:

- model: `RotatE`
- dataset: `FB15k-237`
- evaluation setting: `without`
- analysis unit: `relation-level`
- structural factor: `symmetry`

The current goal is not to prove that certain relations are textbook symmetric relations. The goal is to test whether relation-level symmetry support is associated with predictive multiplicity.

## Current Positioning

At the planning stage, symmetry is currently a stronger candidate than inverse for the next pattern analysis, because:

- it is a single-relation structural property
- it does not require pair-level partner selection
- its definition aligns naturally with the current relation-level thesis framework
- even if the signal later turns out to be weak, the metric itself is conceptually cleaner than the first-round inverse proxy

However, symmetry is still a secondary pattern after `mapping type`, not a replacement for the current main thesis result.

## Main Working Hypothesis

The first-round symmetry hypothesis is:

> stronger symmetry support may be associated with lower predictive multiplicity severity.

In practical terms, this means relations with higher `symmetry_score` may show:

- lower `alpha_r`
- lower `delta_r`
- possibly higher `hits_r`

The first two are the primary focus. `hits_r` is an auxiliary outcome, not the main target of the section.

## Structural Variable

The current primary structural variable is:

- `symmetry_score`

This note deliberately does **not** introduce:

- a formal `antisymmetry_score`

Reason:

- low symmetry does not automatically mean strict antisymmetry
- many relations are simply non-symmetric
- using `1 - symmetry_score` as if it were a real antisymmetry metric would be conceptually misleading

Therefore, the first-round symmetry section should remain a symmetry-score analysis, not a symmetry-vs-antisymmetry taxonomy.

## Planned Implementation Logic

The symmetry-family analysis is relation-level from the beginning.

The intended workflow is:

1. compute relation-level symmetry statistics from the training graph
2. run sanity checks on the symmetry-score distribution
3. merge symmetry statistics with the existing relation-level multiplicity table
4. perform correlation analysis
5. perform bucket-based analysis
6. only if the first-round signal looks promising, consider follow-up control analysis with `mapping_type`

This keeps the first round focused and avoids turning symmetry into an oversized side project.

## Planned Code Path

The intended code path should live in `Multiplicity_rewrite/` and remain separate from `main.py`.

Recommended first-round scripts:

- `Multiplicity_rewrite/symmetry_relation_stats.py`
  computes relation-level symmetry statistics from training triples
- `Multiplicity_rewrite/symmetry_analysis.py`
  merges symmetry statistics with relation-level multiplicity results and computes grouped summaries

Optional follow-up, only if the first round shows a usable signal:

- `Multiplicity_rewrite/symmetry_mapping_interaction_analysis.py`
  examines whether the symmetry effect remains after conditioning on `mapping_type`
- `Multiplicity_rewrite/symmetry_plot.py`
  generates plots for thesis writing

## Code Status

The first-round symmetry code has now been implemented in `Multiplicity_rewrite/`.

Current scripts:

- `Multiplicity_rewrite/symmetry_relation_stats.py`
  computes relation-level symmetry statistics from training triples
- `Multiplicity_rewrite/symmetry_analysis.py`
  merges symmetry statistics with relation-level multiplicity results and computes grouped summaries
- `Multiplicity_rewrite/symmetry_utils.py`
  provides shared helpers for CSV I/O and basic summary statistics

## Planned Outputs

The intended output directory is:

- `results/RotatE_FB15k237/symmetry/`

The planned first-round files are:

- `relation_symmetry_stats.csv`
- `relation_symmetry_multiplicity_merged.csv`
- `correlation_stats.csv`
- `bucket_stats.csv`
- `analysis_summary.txt`

If plotting is later added, additional files may include:

- `scatter_alpha.svg`
- `scatter_delta.svg`
- `scatter_hits.svg`
- `bucket_means.svg`

## Current Outputs

The first-round outputs have now been generated under:

- `results/RotatE_FB15k237/symmetry/`

Current files are:

- `relation_symmetry_stats.csv`
- `symmetry_summary.txt`
- `relation_symmetry_multiplicity_merged.csv`
- `correlation_stats.csv`
- `bucket_stats.csv`
- `analysis_summary.txt`

## Relation-Level Symmetry Table

The first exported symmetry table should contain at least:

- `relation_id`
- `relation_name`
- `train_support`
- `symmetric_supported_edge_count`
- `symmetry_score`

If self-loops turn out to be relevant, the table may later be extended with:

- `self_loop_count`

But this is not required for the minimal first version.

## Planned Merge Table

After merging with the current relation-level multiplicity table, the first analysis table should contain at least:

- `relation_id`
- `relation_name`
- `train_support`
- `symmetry_score`
- `test_support`
- `hits_r`
- `alpha_r`
- `delta_r`

Later enhancements may also include:

- `mapping_type`
- `eligible_support`
- `head_support`
- `tail_support`

But these are not required for the first run.

## Planned Sanity Checks

Before any multiplicity analysis, the symmetry statistics table should be checked for the following:

1. whether `symmetry_score` is highly concentrated at `0`
2. whether there exists a non-empty high-symmetry subgroup
3. whether the distribution has enough spread for meaningful bucketing
4. whether the top high-symmetry relations look semantically plausible
5. whether self-loops are common enough to materially affect the metric

The fifth item matters because a self-loop `(h, r, h)` is automatically symmetry-supported under the current raw definition.

At this stage, the recommended policy is:

- do not preemptively exclude self-loops
- first inspect how often they occur
- then decide whether the implementation needs an adjusted variant

## Planned Statistical Analysis

The first-round symmetry analysis should remain simple and interpretable.

### Correlation

Recommended first-round correlations:

- `symmetry_score` vs `alpha_r`
- `symmetry_score` vs `delta_r`
- `symmetry_score` vs `hits_r`

Spearman correlation is the preferred default because:

- the score distribution may be skewed
- relation-level performance metrics need not follow a linear relationship

### Bucket Analysis

The first bucket design should remain flexible and depend on the observed distribution.

Current preference:

- always preserve a dedicated `zero` bucket if many relations have `symmetry_score = 0`
- for the nonzero portion, prefer a distribution-aware split rather than committing too early to arbitrary fixed thresholds

Examples:

- `zero`
- `nonzero_low`
- `nonzero_mid`
- `nonzero_high`

This is currently preferred over prematurely freezing buckets such as:

- `(0, 0.2]`
- `(0.2, 0.5]`
- `(0.5, 1.0]`

The fixed-threshold version may still be used later if the empirical distribution justifies it.

## Planned Figures

At the current stage, plots are secondary to summary tables.

If the first round shows usable signal, the most useful figures would likely be:

1. bucket-based mean plot for `alpha_r`
2. bucket-based mean plot for `delta_r`
3. optional scatter: `symmetry_score` vs `hits_r`

The current default view is:

- bucket summaries are likely to be more thesis-friendly than raw scatter plots

Therefore, the first coding pass should prioritize tables and summary text before plot polish.

## Planned Interpretation Rules

The symmetry section should be interpreted conservatively.

If the first round shows a usable signal, the safe wording is:

> symmetry score is associated with relation-level multiplicity behavior under the current repeated-run setting.

The section should avoid stronger claims such as:

- symmetry is the cause of multiplicity
- high symmetry always implies low multiplicity
- symmetry alone explains stability

If the first round shows weak or mixed signal, the symmetry section can still remain useful as long as the metric itself is clearly defined and the failure mode is documented honestly.

## Planned Follow-Up Conditions

Only if the first-round signal looks promising should the next step consider additional control analysis.

The most natural follow-up is:

- interaction with `mapping_type`

Reason:

- `mapping_type` is already the strongest thesis result
- symmetry may not be independent from mapping structure
- controlling for `mapping_type` is more relevant than inventing additional symmetry-derived metrics too early

At the current stage, the following are explicitly **not** in the first-round plan:

- formal antisymmetry analysis
- head-tail side-gap analysis
- broad multi-variable regression

These would only be justified if the first round yields an ambiguous but nontrivial signal.

## Current Status

Current status:

- symmetry definitions and thesis positioning have been discussed
- the first-round symmetry scripts have been implemented
- the first raw symmetry table has been generated
- the first merge analysis against relation-level multiplicity results has been completed
- the self-loop issue has moved from a theoretical concern to an empirical caveat

Therefore, this section is currently at the “first raw symmetry analysis completed” stage.

## First-Round Distribution Summary

The first sanity check shows that the raw symmetry score is mathematically usable, but highly sparse.

Current summary:

- total relations: `237`
- `symmetry_score = 0`: `193`
- `symmetry_score > 0.5`: `27`
- relations with `self_loop_count > 0`: `17`
- total self loops: `1625`

Distribution summary for raw `symmetry_score`:

- min: `0.0000`
- 25th percentile: `0.0000`
- median: `0.0000`
- 75th percentile: `0.0000`
- 90th percentile: `0.7903`
- max: `1.0000`

This means the first-round distribution is extremely zero-heavy, with a relatively small but nonempty high-symmetry tail.

## First-Round Self-Loop Finding

The self-loop concern turned out to be real and nontrivial.

The most important observation is:

- several top raw-symmetry relations are almost entirely driven by self-loops

Examples include:

- `/education/educational_institution/campuses`
- `/education/educational_institution_campus/educational_institution`
- `/location/hud_county_place/place`

For these relations:

- raw `symmetry_score = 1.0`
- but `symmetry_score_excluding_self_loops = 0.0`

This is the most important methodological caveat from the first run.

Therefore, the current raw symmetry metric should not be interpreted naively at the top end without checking whether the score is mainly created by self-loops.

## First-Round Multiplicity Association

Using the raw `symmetry_score`, the first-round global correlations are weak.

For `test_support >= 10`:

- `symmetry_score` vs `hits_r`: `0.0800`
- `symmetry_score` vs `alpha_r`: `0.0389`
- `symmetry_score` vs `delta_r`: `0.0161`

So the raw score does not currently support a strong first-order claim of the form:

> higher symmetry strongly predicts lower multiplicity.

## Excluding-Self Auxiliary Check

Although the primary first-round analysis still uses raw `symmetry_score`, the implementation also exported an auxiliary version:

- `symmetry_score_excluding_self_loops`

This was added only for diagnosis, not as the officially frozen main metric.

The auxiliary Spearman check suggests:

- `symmetry_score_excluding_self_loops` has near-zero association with `hits_r`
- but a weak positive association with `alpha_r` and `delta_r`

For `test_support >= 10`:

- excluding-self vs `hits_r`: `0.0122`
- excluding-self vs `alpha_r`: `0.1310`
- excluding-self vs `delta_r`: `0.1292`

This is not yet a strong result, but it already indicates that:

- once the self-loop inflation is removed, the symmetry story does not become a simple “more symmetry means more stability” pattern

## First-Round Interpretation

At the current stage, the safest reading is:

- the symmetry score is usable as a relation-level structural variable
- but the raw definition is clearly sensitive to self-loops
- the global relation between symmetry and multiplicity is weak in the first run
- therefore the section is not yet ready for a strong thesis claim

This does not mean the symmetry direction has failed.

What it means is:

- the first run behaved primarily like a metric audit and sanity-check round
- the self-loop issue now needs to be resolved explicitly before symmetry can be interpreted with confidence

## Decision After the Raw Run

After the first raw run, the symmetry line should not continue with the raw metric as the main definition.

The current decision is:

- keep raw `symmetry_score` only as a diagnostic sanity-check quantity
- switch the main analysis metric to `symmetry_score_excluding_self_loops`

Reason:

- the raw metric can assign extremely high symmetry to relations whose apparent support is created almost entirely by self-loops
- this is too misleading for a thesis-level main result

## V2 Rerun With Excluding-Self Symmetry

The second-round symmetry analysis has now been implemented and executed.

### New Code Path

The new second-round script is:

- `Multiplicity_rewrite/symmetry_analysis_v2.py`

The first-round scripts remain unchanged:

- `symmetry_relation_stats.py`
- `symmetry_analysis.py`

This split preserves:

- the raw metric audit as a reproducible first round
- the excluding-self metric as the stricter second round

### New Output Directory

The v2 outputs are stored under:

- `results/RotatE_FB15k237/symmetry_v2/`

Current files are:

- `relation_symmetry_multiplicity_merged_v2.csv`
- `correlation_stats_v2.csv`
- `bucket_stats_v2.csv`
- `analysis_summary_v2.txt`

### V2 Metric and Bucket Design

The main v2 metric is:

- `symmetry_score_excluding_self_loops`

The bucket design was deliberately simplified because the empirical distribution is too sparse for inverse-style fine-grained bucketing.

Current buckets are:

- `zero`
- `weak_nonzero`
- `high_symmetry`

where:

- `weak_nonzero` means `(0, 0.5]`
- `high_symmetry` means `(0.5, 1.0]`

### Distribution After Excluding Self-Loops

After switching to the excluding-self metric:

- `symmetry_score = 0`: `207`
- `high_symmetry (> 0.5)`: `24`

For `test_support >= 10`:

- `zero`: `164`
- `weak_nonzero`: `6`
- `high_symmetry`: `12`

This confirms that the symmetry variable is not smoothly continuous in practice.

Instead, it behaves more like:

- a very large zero group
- a tiny weak-nonzero residue
- a compact high-symmetry subgroup

### Main V2 Result

The excluding-self rerun does not support the original hoped-for direction.

For `test_support >= 10`:

- `symmetry_score` vs `hits_r`: `0.0122`
- `symmetry_score` vs `alpha_r`: `0.1310`
- `symmetry_score` vs `delta_r`: `0.1292`

Therefore, even after fixing the self-loop problem, the symmetry section still does not support a clean claim that:

> stronger symmetry implies lower multiplicity.

### Bucket-Level Result

The bucket means are also not encouraging for a positive symmetry story.

For `test_support >= 10`:

- `zero`:
  - `hits_mean = 0.5815`
  - `alpha_mean = 0.2294`
  - `delta_mean = 0.1331`
- `weak_nonzero`:
  - `hits_mean = 0.5047`
  - `alpha_mean = 0.3610`
  - `delta_mean = 0.2236`
- `high_symmetry`:
  - `hits_mean = 0.5924`
  - `alpha_mean = 0.3735`
  - `delta_mean = 0.2341`

This means:

- the high-symmetry subgroup is not more stable than the zero-symmetry group
- if anything, the high-symmetry subgroup currently looks more multiplicity-prone on average

### High-Symmetry Case Reading

The high-symmetry subgroup is also quite heterogeneous.

There are some stable high-symmetry relations, for example:

- `/award/award_winning_work/awards_won./award/award_honor/honored_for`
- `/government/legislative_session/members./government/government_position_held/legislative_sessions`

But there are also very unstable high-symmetry relations, for example:

- `/music/performance_role/regular_performances./music/group_membership/role`
- `/music/performance_role/track_performances./music/track_contribution/role`
- `/base/popstra/celebrity/dated./base/popstra/dated/participant`
- `/base/popstra/celebrity/friendship./base/popstra/friendship/participant`

So the current high-symmetry subgroup is not a clean “good” subgroup in the way the strongest inverse-v2 subgroup was.

### Mapping-Type Concentration

The high-symmetry subgroup is also heavily concentrated in one structural regime.

For `test_support >= 10`:

- `high_symmetry` relations: `12`
- all `12` are `M-N`

This is an important warning sign.

It means the current symmetry pattern is likely entangled with:

- relation semantics
- `M-N` structure
- and possibly relation density

rather than acting as an independent structural explanation.

### Current Interpretation After V2

At the current stage, the safest interpretation is:

- symmetry is not currently giving a useful standalone explanatory pattern for multiplicity
- once self-loops are handled properly, the remaining signal is sparse and structurally concentrated
- the excluding-self metric does not reveal a clean low-multiplicity subgroup
- therefore symmetry should not be promoted as a main positive result under the current setup

### Current Decision After V2

The recommended status is now:

- keep `mapping type` as the stable main structural result
- keep inverse as the more promising exploratory secondary line
- treat symmetry as a weak or negative result unless later cross-model evidence changes the picture

At this stage, the best next use of symmetry is not deeper analysis on `RotatE` alone, but:

- later cross-model comparison, especially against `TransE`

because model-class expressiveness may matter more here than within-model relation-level variation alone.

## Immediate Next Step

The immediate next step for symmetry is no longer another within-`RotatE` refinement.

Instead, the most informative follow-up would likely be:

1. keep the current `RotatE` symmetry result as a completed baseline
2. later run the same excluding-self symmetry analysis on `TransE`
3. then compare whether model-class differences are more informative than relation-level variation within `RotatE`

## TransE Follow-Up Has Now Been Run

The planned `TransE` comparison has now been executed.

This means the symmetry section is no longer only a `RotatE`-internal note. It now includes a first cross-model comparison under the same dataset and repeated-run multiplicity setup.

## TransE Setup

The `TransE` comparison uses:

- model: `TransE`
- dataset: `FB15k-237`
- experiment folder: `LibKGE/local/multiplicity/TransE_FB15k237_N`
- repeated runs: `seed_0` to `seed_7`

The comparison deliberately reused existing repeated runs rather than retraining from scratch.

Therefore, this follow-up did **not** require running `main.py` again.

Instead, the workflow was:

1. export the combined relation-level multiplicity table directly from the existing repeated runs
2. reuse the same symmetry statistics table generation
3. run both the raw symmetry analysis and the excluding-self v2 analysis

## Additional Code Used For TransE

The `TransE` follow-up required one more export step:

- `Multiplicity_rewrite/relation_multiplicity_combined_export.py`

This script exports the combined relation-level multiplicity table in the same format used by the symmetry merge analysis.

There was also a small infrastructure adjustment:

- `Multiplicity_rewrite/multiplicity_utils.py`

The helper that restores stored runs now falls back to CPU when the original checkpoint config points to CUDA but no visible GPU is available in the current environment.

This is an implementation detail rather than a thesis result, but it matters for reproducibility of the `TransE` comparison.

## TransE Output Directories

The `TransE` outputs are stored under:

- `results/TransE_FB15k237_N/symmetry/`
- `results/TransE_FB15k237_N/symmetry_v2/`

The exported combined multiplicity table is:

- `results/TransE_FB15k237_N/mapping_type/combined/relation_metrics_num7_agg7_k10.csv`

## Raw TransE Symmetry Result

The raw symmetry analysis for `TransE` largely reproduces the same metric caveat already seen in `RotatE`.

Raw summary:

- merged relations: `237`
- `symmetry_score = 0`: `193`
- `symmetry_score > 0.5`: `27`
- relations with `self_loop_count > 0`: `17`

So the raw symmetry distribution is a property of the training graph, not of the model, and the same self-loop warning still applies.

For `test_support >= 10`, the raw `TransE` correlations are still weak:

- raw `symmetry_score` vs `hits_r`: `0.0919`
- raw `symmetry_score` vs `alpha_r`: `-0.0307`
- raw `symmetry_score` vs `delta_r`: `-0.0331`

This means the raw metric remains unsuitable as a thesis-level main definition even in the `TransE` comparison.

## TransE V2 Result With Excluding-Self Symmetry

The more meaningful comparison is the v2 analysis using:

- `symmetry_score_excluding_self_loops`

The distribution after excluding self-loops remains identical to the graph-side `RotatE` baseline:

- `symmetry_score = 0`: `207`
- `high_symmetry (> 0.5)`: `24`

For `test_support >= 10`:

- `zero`: `164`
- `weak_nonzero`: `6`
- `high_symmetry`: `12`

So the structural symmetry variable is still extremely sparse and close to a zero-vs-high subgroup pattern.

## TransE V2 Correlation Summary

For `test_support >= 10`, the excluding-self `TransE` correlations are:

- `symmetry_score` vs `hits_r`: `0.0117`
- `symmetry_score` vs `alpha_r`: `0.0425`
- `symmetry_score` vs `delta_r`: `0.0520`

These values are still weak.

Therefore, even under `TransE`, symmetry does not become a strong global explanatory variable for multiplicity.

## TransE V2 Bucket Summary

For `test_support >= 10`, the `TransE` v2 bucket means are:

- `zero`:
  - `hits_mean = 0.5605`
  - `alpha_mean = 0.3307`
  - `delta_mean = 0.1838`
- `weak_nonzero`:
  - `hits_mean = 0.4725`
  - `alpha_mean = 0.4436`
  - `delta_mean = 0.2736`
- `high_symmetry`:
  - `hits_mean = 0.5742`
  - `alpha_mean = 0.3512`
  - `delta_mean = 0.2119`

This is slightly less negative than the `RotatE` v2 picture, because the `high_symmetry` subgroup in `TransE` does not look as severely multiplicity-prone as it did in `RotatE`.

However, it is still not a genuinely positive symmetry result:

- `high_symmetry` is not cleaner than `zero`
- `alpha_mean` and `delta_mean` remain higher than the `zero` group

So the cross-model comparison does **not** rescue the original hypothesis.

## Direct RotatE vs TransE Comparison

Using the same excluding-self definition and `test_support >= 10` threshold:

- `RotatE`
  - `zero`: `hits=0.5815`, `alpha=0.2294`, `delta=0.1331`
  - `high_symmetry`: `hits=0.5924`, `alpha=0.3735`, `delta=0.2341`
- `TransE`
  - `zero`: `hits=0.5605`, `alpha=0.3307`, `delta=0.1838`
  - `high_symmetry`: `hits=0.5742`, `alpha=0.3512`, `delta=0.2119`

This suggests three points.

First:

- the symmetry variable itself is not model-dependent; the sparse zero-heavy distribution comes from the graph

Second:

- neither model shows a clean “more symmetry implies lower multiplicity” pattern

Third:

- the penalty of the `high_symmetry` subgroup relative to the `zero` group appears somewhat milder in `TransE` than in `RotatE`
- but the direction is still not strong enough to support a positive thesis claim

## High-Symmetry Subgroup Under TransE

The `TransE` high-symmetry subgroup remains heterogeneous.

Stable or relatively favorable examples include:

- `/award/award_winning_work/awards_won./award/award_honor/honored_for`
- `/government/legislative_session/members./government/government_position_held/legislative_sessions`
- `/award/award_nominated_work/award_nominations./award/award_nomination/nominated_for`

Unstable examples still remain:

- `/music/performance_role/regular_performances./music/group_membership/role`
- `/music/performance_role/track_performances./music/track_contribution/role`
- `/base/popstra/celebrity/friendship./base/popstra/friendship/participant`

So even after moving to a different model class, the high-symmetry subgroup is still not a uniformly low-multiplicity group.

## Mapping-Type Concentration Still Holds

The concentration pattern also remains.

For `test_support >= 10`:

- `high_symmetry` relations in `TransE`: `12`
- all `12` are `M-N`

So the current symmetry signal is still strongly entangled with the `M-N` regime rather than behaving like an independent structural axis.

## Current Cross-Model Interpretation

After adding the `TransE` comparison, the safest overall interpretation is:

- the raw symmetry metric is mainly useful for exposing the self-loop caveat
- the excluding-self metric is conceptually cleaner and should remain the main definition
- but under both `RotatE` and `TransE`, symmetry remains a weak global predictor of multiplicity
- the high-symmetry subgroup is sparse, heterogeneous, and concentrated in `M-N`
- therefore symmetry should be recorded mainly as a weak or negative result in the current thesis

This is still useful.

The section now contributes:

- a clearly defined symmetry metric
- an explicit methodological caveat about self-loops
- a negative cross-model result showing that the problem is not merely an artifact of one model family

## Current Decision After The TransE Comparison

The recommended thesis positioning is now:

- `mapping type` remains the main structural result
- `inverse` remains the stronger exploratory secondary line
- `symmetry` should be kept as a documented weak/negative result, supported by both `RotatE` and `TransE`

At this point, deeper analysis on symmetry is unlikely to be worth the time unless a later writing need specifically requires:

- a short appendix-style visualization
- or a brief model-comparison paragraph in the thesis text
