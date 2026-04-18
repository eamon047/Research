# Thesis Symmetry Experiment

## Purpose of This Note

This note records the planned setup, implementation path, output structure, and interpretation rules for the symmetry-family analysis under the thesis main line.

Unlike `thesis_theory.md`, this file is not meant to freeze abstract definitions forever. It is a working experiment note for thesis writing and iteration.

At the current stage, this document should be treated as a prepared experiment record rather than a completed result note.

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
- the main conceptual risk around fake antisymmetry labeling has been identified
- the self-loop issue has been identified as a required sanity check
- the first-round experiment has not yet been implemented
- no symmetry-specific CSVs or plots have yet been generated

Therefore, this section is currently at the “pre-registration / implementation planning” stage.

## Immediate Next Step

The immediate next step should be:

1. implement `symmetry_relation_stats.py`
2. compute the first raw symmetry table from the training graph
3. inspect the score distribution and self-loop prevalence
4. only then decide the final bucket design for the first-round analysis
