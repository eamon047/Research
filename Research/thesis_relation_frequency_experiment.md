# Thesis Relation-Frequency Experiment

## Purpose of This Note

This note records the experimental scope, implementation path, and interpretation rules for the relation-frequency analysis under the current thesis main line.

Unlike `thesis_theory.md`, this file is not meant to freeze abstract definitions forever. It is a working experiment note for thesis writing and iteration.

At the current stage, this document should be treated as a maintained experiment record that already includes:

- the `RotatE` base analysis
- the `mapping type × frequency` interaction analysis
- the `TransE` comparison
- the current control-variable interpretation

Any sections titled as "planned" below should now be read as historical design
notes for reproducibility. The current thesis status is given by the later
implemented-output and `TransE` comparison sections.

## Current Positioning

The central decision for this section is already fixed:

- `relation frequency` is **not** treated as a fourth relation pattern
- it is treated as a relation-level support / sparsity factor
- its main role is to serve as a baseline control variable

Therefore, this section is conceptually different from:

- `mapping type`
- `inverse-like support`
- `symmetry`

Its purpose is not to add another structural pattern, but to test whether simple support differences can explain part of the observed multiplicity behavior.

## Main Thesis Role

The relation-frequency section should serve two purposes.

### 1. Baseline validation

Check whether low-support relations are more multiplicity-prone under the current thesis setting.

### 2. Control-axis analysis

Check whether the main `mapping type` result remains meaningful after relation support / sparsity is brought into the analysis explicitly.

This second purpose is the more important one.

## Current Scope

The current relation-frequency study uses the following fixed thesis setting:

- dataset: `FB15k-237`
- models: `RotatE`, `TransE`
- evaluation setting: `without`
- analysis unit: `relation-level`
- factor type: `support / sparsity factor`

The main thesis purpose is no longer to test whether `TransE` should be added. That replication has already been completed, and the section is now written as a control-variable analysis rather than a still-open experiment plan.

## Core Variables

The first-round section should explicitly track:

- `train_frequency`
- `log_train_frequency`

where:

- `train_frequency` is the number of training triples containing the relation
- `log_train_frequency = log(train_frequency + 1)`

Although `train_frequency` is numerically close to the already existing `train_support`, the current section keeps the frequency naming because:

- it aligns with the original paper’s terminology
- it supports a cleaner support / sparsity interpretation

## Main Working Hypotheses

### H1: Support hypothesis

Relations with lower `log_train_frequency` may show:

- higher `alpha_r`
- higher `delta_r`
- possibly lower `hits_r`

The first two are the primary focus. `hits_r` is secondary.

### H2: Mapping-type independence question

The current mapping-type result may or may not be reducible to support differences.

The key question is:

> is the mapping-type effect still visible after relation frequency is explicitly considered?

This is the main reason why relation frequency is worth doing in the thesis.

## What This Section Is Not

The current plan explicitly does **not** treat relation frequency as:

- a new logical relation pattern
- a geometry-driven pattern family
- a replacement for mapping type

The section also does **not** include, in the first round:

- regression as the main analysis entry
- a large combined analysis with inverse and symmetry

These are intentionally excluded to keep the scope clean.

## Planned Implementation Logic

The current recommended workflow has two layers.

### Layer 1: Base relation-level frequency analysis

1. compute `train_frequency` and `log_train_frequency` from the training graph
2. merge them with the current relation-level multiplicity table
3. run correlation analysis
4. run bucket-based analysis

This layer answers:

> does relation frequency itself show a relation-level association with multiplicity?

### Layer 2: Mapping type × frequency analysis

This is the real thesis-value layer.

The goal is:

> check whether mapping type is merely a proxy for relation frequency

The most important current design decision is:

- the combined relation-level table can be used in Layer 1
- but the main `mapping type × frequency` analysis should be based on the **by-side** table

Reason:

- the strongest mapping-type result is already side-dependent
- if this section falls back only to the combined table, it will weaken the main thesis argument

## Planned Code Path

The frequency-family analysis should live in `Multiplicity_rewrite/` and remain separate from `main.py`.

Recommended first-round scripts:

- `Multiplicity_rewrite/relation_frequency_stats.py`
  computes relation-level frequency statistics from training triples
- `Multiplicity_rewrite/relation_frequency_analysis.py`
  merges frequency statistics with relation-level multiplicity results and computes grouped summaries
- `Multiplicity_rewrite/relation_frequency_mapping_interaction.py`
  analyzes the interaction between frequency and mapping type, with by-side results as the main target

## Planned Outputs

The intended output directory for the first round is:

- `results/RotatE_FB15k237/relation_frequency/`

Recommended first-round files:

- `relation_frequency_stats.csv`
- `relation_frequency_multiplicity_merged.csv`
- `correlation_stats.csv`
- `bucket_stats.csv`
- `analysis_summary.txt`

Recommended second-layer files:

- `mapping_interaction/correlation_by_mapping_type.csv`
- `mapping_interaction/bucket_stats_by_mapping_type.csv`
- `mapping_interaction/summary.txt`

If plots are later added, they may include:

- `logfreq_vs_alpha.svg`
- `logfreq_vs_delta.svg`
- `bucket_means.svg`
- `mapping_type_by_frequency.svg`

## Planned Base Merge Table

The first merged table should contain at least:

- `relation_id`
- `relation_name`
- `train_frequency`
- `log_train_frequency`
- `mapping_type`
- `test_support`
- `hits_r`
- `alpha_r`
- `delta_r`

Later additions are possible, but not required for the first run.

## Planned Statistical Analysis

The first round should remain simple and interpretable.

### Correlation

Recommended first-round correlations:

- `log_train_frequency` vs `hits_r`
- `log_train_frequency` vs `alpha_r`
- `log_train_frequency` vs `delta_r`

Spearman correlation is the preferred default because:

- frequency is long-tailed
- relation-level multiplicity metrics need not have a linear relationship with support

### Thresholding

To keep the result comparable with other sections, the current default thresholds should include:

- all relations
- `test_support >= 5`
- `test_support >= 10`

### Bucket Analysis

The first bucket design should be distribution-aware.

Current recommendation:

- use `log_train_frequency`
- split nontrivially by quantiles
- avoid prematurely freezing arbitrary hard-coded thresholds

A simple and safe first version is:

- low frequency
- medium frequency
- high frequency

or quartiles if the observed distribution supports it.

## Planned Mapping-Type Interaction

This is the most important follow-up after the base frequency analysis.

Two possible views are acceptable:

### View A: Within each mapping type, inspect frequency association

For each mapping type, compute:

- `log_train_frequency` vs `hits_r`
- `log_train_frequency` vs `alpha_r`
- `log_train_frequency` vs `delta_r`

### View B: Within each frequency bucket, inspect mapping-type difference

For example:

- in low-frequency relations, do mapping types still differ clearly in `alpha_r / delta_r`?
- in high-frequency relations, does the mapping-type gap shrink or remain?

The current expectation is not to prove that frequency is stronger than mapping type.

The goal is narrower:

> show that the mapping-type result is not merely a simple frequency effect.

## Planned Figures

Plots are useful here, but they should remain secondary to the summary tables in the first implementation pass.

If the first round shows a usable signal, the most valuable figures would be:

1. `log_train_frequency` vs `alpha_r`
2. `log_train_frequency` vs `delta_r`
3. bucket-based mean plot
4. mapping type × frequency bucket figure

The key figure, if only one can be kept later, is likely:

- mapping type × frequency bucket

because it connects the frequency control variable directly to the strongest thesis result.

## Planned Interpretation Rules

The relation-frequency section should be interpreted conservatively.

If the first round shows a usable signal, the safe wording is:

> relation frequency is associated with relation-level multiplicity behavior under the current repeated-run setting.

The section should avoid stronger claims such as:

- frequency alone explains multiplicity
- support is the only reason mapping types differ
- low frequency automatically implies instability

## Current Code Status

The first-round `RotatE` relation-frequency pipeline has now been implemented in `Multiplicity_rewrite/`.

Current scripts:

- `Multiplicity_rewrite/relation_frequency_utils.py`
- `Multiplicity_rewrite/relation_frequency_stats.py`
- `Multiplicity_rewrite/relation_frequency_analysis.py`
- `Multiplicity_rewrite/relation_frequency_mapping_interaction.py`

## Current Outputs

The first-round outputs have now been generated under:

- `results/RotatE_FB15k237/relation_frequency/`

Current files are:

- `relation_frequency_stats.csv`
- `frequency_summary.txt`
- `relation_frequency_multiplicity_merged.csv`
- `correlation_stats.csv`
- `bucket_stats.csv`
- `bucket_bounds.csv`
- `analysis_summary.txt`
- `mapping_interaction/relation_frequency_by_side_merged.csv`
- `mapping_interaction/correlation_by_side_and_mapping_type.csv`
- `mapping_interaction/bucket_stats_by_side_and_mapping_type.csv`
- `mapping_interaction/bucket_bounds_by_side.csv`
- `mapping_interaction/summary.txt`

## First-Round Frequency Distribution

The relation-frequency distribution is strongly long-tailed, as expected.

Current summary:

- total relations: `237`
- `train_frequency = 0`: `0`

`train_frequency` distribution:

- min: `37`
- 25th percentile: `179`
- median: `373`
- 75th percentile: `859`
- 90th percentile: `2693.4`
- max: `15989`

`log_train_frequency` distribution:

- min: `3.6376`
- 25th percentile: `5.1930`
- median: `5.9243`
- 75th percentile: `6.7569`
- 90th percentile: `7.8989`
- max: `9.6797`

So the log transform is justified and should remain the default analytical form.

## First-Round Base Result

The base combined relation-level result does **not** support the original naive support hypothesis in a simple way.

For `test_support >= 10`:

- `Spearman(log_train_frequency, hits_r) = -0.2865`
- `Spearman(log_train_frequency, alpha_r) = 0.1850`
- `Spearman(log_train_frequency, delta_r) = 0.0553`

This means the current `RotatE` relation-level result is not:

> lower frequency leads to lower accuracy and higher multiplicity

Instead, the observed tendency is closer to:

- higher-frequency relations have somewhat lower `hits_r`
- higher-frequency relations also show slightly higher `alpha_r`
- the relation with `delta_r` is weak

This is an important result because it differs from the most naive expectation and therefore should not be forced into a simplistic low-support story.

## Bucket-Level Base Result

The bucket summary tells the same story.

For `test_support >= 10`:

- `low_frequency`:
  - `hits_mean = 0.6403`
  - `alpha_mean = 0.2088`
  - `delta_mean = 0.1364`
- `mid_frequency`:
  - `hits_mean = 0.6066`
  - `alpha_mean = 0.2494`
  - `delta_mean = 0.1459`
- `high_frequency`:
  - `hits_mean = 0.4925`
  - `alpha_mean = 0.2717`
  - `delta_mean = 0.1460`

So the first-round base result is not a clean “low frequency is worse” pattern.

At the combined relation level, the direction is actually closer to the opposite for `hits_r`, and only weakly positive for multiplicity.

## Why The Base Result Should Not Be Overread

The most likely interpretation is not that “more data makes relations worse.”

A more careful reading is:

- high-frequency relations are not randomly distributed across the graph
- they are more concentrated in dense and structurally difficult regimes
- therefore the base combined frequency correlation is confounded by relation structure

This is exactly why the second layer of the analysis matters.

## Mapping-Type Composition Across Frequency Buckets

The frequency buckets are structurally imbalanced.

For `test_support >= 10`:

- `low_frequency`:
  - `1-1: 3`
  - `1-N: 12`
  - `M-1: 27`
  - `M-N: 19`
- `mid_frequency`:
  - `1-1: 4`
  - `1-N: 6`
  - `M-1: 22`
  - `M-N: 28`
- `high_frequency`:
  - `1-1: 0`
  - `1-N: 4`
  - `M-1: 14`
  - `M-N: 43`

This is already enough to show that the combined frequency result is heavily entangled with mapping structure.

The `high_frequency` group is dominated by `M-N`, while `1-1` disappears entirely.

So if we stopped at the base correlation, we would be mixing support and structural difficulty together.

## Mapping Type × Frequency Result

This is the real thesis-value part of the section.

The by-side interaction analysis shows that the main mapping-type result remains visible inside frequency strata.

### Head Side

For `test_support >= 10`:

- `low_frequency`:
  - `hits_r`: `1-N > M-N > 1-1 > M-1`
  - `alpha_r`: `1-N < M-N < 1-1 < M-1`
  - `delta_r`: `1-N < M-N < 1-1 < M-1`
- `mid_frequency`:
  - `hits_r`: `1-N > 1-1 > M-N > M-1`
  - `alpha_r`: `1-N < 1-1 < M-N < M-1`
  - `delta_r`: `1-N < 1-1 < M-N < M-1`
- `high_frequency`:
  - `hits_r`: `M-N ≈ 1-N > M-1`
  - `alpha_r`: `1-N < M-N < M-1`
  - `delta_r`: `M-N ≈ 1-N < M-1`

Even though the exact ordering is not perfectly identical in every bucket, the core directional thesis result remains:

- on the `head` side, `M-1` is still the hardest regime
- `1-N` remains among the easiest regimes

### Tail Side

For `test_support >= 10`:

- `low_frequency`:
  - `hits_r`: `M-1 > M-N > 1-1 > 1-N`
  - `alpha_r`: `M-1 < M-N < 1-1 < 1-N`
  - `delta_r`: `M-1 < M-N < 1-1 < 1-N`
- `mid_frequency`:
  - `hits_r`: `M-1 > 1-1 > M-N > 1-N`
  - `alpha_r`: `M-1 < M-N ≈ 1-1 < 1-N`
  - `delta_r`: `M-1 < 1-1 < M-N < 1-N`
- `high_frequency`:
  - `hits_r`: `M-1 > M-N > 1-N`
  - `alpha_r`: `M-1 < M-N < 1-N`
  - `delta_r`: `M-1 < M-N < 1-N`

This is even cleaner than the head side.

The main directional mapping-type result clearly survives inside each frequency bucket.

## Within-Mapping-Type Frequency Correlations

The within-type correlations also help explain the combined result.

For `test_support >= 10`:

- `1-N`, head side:
  - `Spearman(log_train_frequency, hits_r) = -0.5094`
  - `Spearman(log_train_frequency, alpha_r) = 0.5147`
  - `Spearman(log_train_frequency, delta_r) = 0.4894`
- `1-N`, tail side:
  - `Spearman(log_train_frequency, hits_r) = -0.5133`
  - `Spearman(log_train_frequency, alpha_r) = 0.3854`
  - `Spearman(log_train_frequency, delta_r) = 0.0631`
- `M-1`, head side:
  - `Spearman(log_train_frequency, hits_r) = -0.4431`
  - `Spearman(log_train_frequency, alpha_r) = 0.3592`
  - `Spearman(log_train_frequency, delta_r) = 0.1748`
- `M-N`, head side:
  - `Spearman(log_train_frequency, hits_r) = -0.3491`
  - `Spearman(log_train_frequency, alpha_r) = 0.2123`
  - `Spearman(log_train_frequency, delta_r) = 0.1148`

So the current thesis setting does not show a universal beneficial frequency effect even *within* mapping types.

This reinforces the idea that frequency should be treated as:

- an explanatory control variable
- not a simple monotonic predictor

## First-Round Interpretation

The first `RotatE` run supports a more precise thesis reading than the original naive support hypothesis.

The safest interpretation is:

- relation frequency is relevant and should be kept in the thesis
- but it does not form a simple “low support causes multiplicity” story under the current relation-level setting
- the base combined result is structurally confounded
- once frequency is used as a control axis, the mapping-type result remains clearly visible

This is actually a stronger thesis outcome than a trivial negative correlation would have been.

Because the real thesis-value sentence now becomes:

> mapping type is not merely a proxy for relation frequency.

## Current Decision After The First RotatE Run

The current recommended status is:

- keep relation frequency in the thesis
- present it as a support / sparsity control variable, not as a pattern
- report that the base relation-level frequency effect is not simply aligned with the naive low-support hypothesis
- emphasize that the main mapping-type result survives frequency stratification

At this stage, the relation-frequency line already looks useful enough to keep.

## Historical Next Step

The immediate next step at that stage was no longer to ask whether this section should exist.

That is now answered.

The next reasonable options were:

1. polish the current `RotatE` result into thesis-ready wording
2. replicate the same control-variable analysis on `TransE`
3. optionally add one or two lightweight figures after the textual interpretation is stabilized

The `TransE` follow-up has now been completed and is recorded below.

## TransE Follow-Up Has Now Been Completed

The planned `TransE` comparison has now also been run.

This means the relation-frequency section is no longer supported only by:

- `RotatE + FB15k-237`

It now also has a first cross-model check under:

- `TransE + FB15k-237`

using the same relation-level thesis setting.

## TransE Outputs

The `TransE` outputs are now stored under:

- `results/TransE_FB15k237/relation_frequency/`
- `results/TransE_FB15k237/relation_frequency/mapping_interaction/`

## TransE Base Result

The `TransE` base relation-level result does not move toward the original paper’s simple negative frequency correlation either.

For `test_support >= 10`:

- `Spearman(log_train_frequency, hits_r) = -0.2734`
- `Spearman(log_train_frequency, alpha_r) = 0.1583`
- `Spearman(log_train_frequency, delta_r) = 0.0273`

This is extremely close in shape to the `RotatE` result:

- `RotatE`: `hits = -0.2865`, `alpha = 0.1850`, `delta = 0.0553`
- `TransE`: `hits = -0.2734`, `alpha = 0.1583`, `delta = 0.0273`

So under the current thesis setting, the simple original-paper expectation:

> higher relation frequency implies lower multiplicity

is **not** reproduced by either model.

## TransE Bucket Result

The bucket means also remain structurally similar to the `RotatE` case.

For `test_support >= 10`:

- `low_frequency`:
  - `hits_mean = 0.6166`
  - `alpha_mean = 0.3011`
  - `delta_mean = 0.1899`
- `mid_frequency`:
  - `hits_mean = 0.5888`
  - `alpha_mean = 0.3360`
  - `delta_mean = 0.1868`
- `high_frequency`:
  - `hits_mean = 0.4707`
  - `alpha_mean = 0.3705`
  - `delta_mean = 0.1888`

So the combined relation-level picture remains:

- higher-frequency relations tend to have lower `hits_r`
- `alpha_r` does not go down
- `delta_r` changes very little

Again, this is the opposite of a naive low-support explanation.

## TransE Mapping Type × Frequency Result

The by-side `mapping type × frequency` analysis remains the most important part of the section.

The main mapping-type directional result still survives inside frequency strata.

For `test_support >= 10`:

- `head` side:
  - low frequency: `1-N` remains best, `M-1` remains worst
  - mid frequency: `1-N / 1-1` remain strongest, `M-1` remains worst
  - high frequency: `M-N / 1-N` remain clearly above `M-1`
- `tail` side:
  - low frequency: `M-1` remains best, `1-N` remains worst
  - mid frequency: `M-1 / 1-1` remain strongest, `1-N` remains worst
  - high frequency: `M-1` remains best, `1-N` remains worst

So the central control-variable conclusion survives the model change:

> mapping type is not merely a proxy for relation frequency.

## Updated Cross-Model Interpretation

After adding the `TransE` comparison, the safest overall interpretation becomes:

- the original paper’s weak negative relation-frequency correlation is not reproduced in the current thesis setting
- this is not just a `RotatE` artifact, because `TransE` behaves similarly
- the most likely reason is that the current thesis setting is narrower than the paper’s frequency study:
  - the paper pools relation-specific subsets across multiple models and datasets
  - the current thesis fixes the setting to `FB15k-237` and repeated runs of one model family at a time
- the relation-level combined frequency effect is structurally confounded
- once frequency is used as a control axis, the by-side mapping-type result remains robust

This actually strengthens the current thesis positioning of relation frequency.

It is not a clean main result by itself, but it is a useful control variable that helps defend the main mapping-type claim.

## Updated Current Status

The recommended thesis positioning is now:

- keep relation frequency as a support / sparsity control variable
- explicitly note that the simple original-paper negative trend does not directly carry over to the current thesis setting
- emphasize that the most important finding is the persistence of the mapping-type effect after frequency stratification

At this point, the relation-frequency section is already useful enough to keep in the thesis.
