# Thesis Mapping-Type Experiment

## Purpose of This Note

This note records the experimental setup, code path, output files, and current findings for the mapping-type analysis under the thesis main line.

Unlike `thesis_theory.md`, this file is not meant to freeze abstract definitions forever. It is a working experiment note for thesis writing and iteration.

## Current Scope

At the current stage, the scope is intentionally narrow:

- model: `RotatE`
- dataset: `FB15k-237`
- evaluation setting: `without`
- analysis unit: `relation-level`
- structural factor: `mapping type`

The current goal is not to study voting mitigation. The goal is to understand whether predictive multiplicity is associated with relation mapping structure.

## Why the `without` Setting Is Used

For the thesis main line, the `without` setting is the most appropriate starting point because it reflects raw multiplicity among repeated runs of the same model family.

This makes the interpretation cleaner:

- we analyze disagreement before voting-based mitigation
- we avoid mixing structural analysis with aggregation effects
- we stay closer to the question of whether multiplicity itself is structurally non-uniform

Therefore, the current mapping-type study uses:

- `baseline = without`

and does not treat `major`, `borda`, or `range` as part of the primary result.

## Code Entry Points

The current code path lives in `Multiplicity_rewrite/`.

Relevant scripts:

- `Multiplicity_rewrite/relation_mapping_analysis.py`
  exports relation-level CSVs for mapping-type analysis
- `Multiplicity_rewrite/support_distribution_analysis.py`
  summarizes support distributions and candidate thresholds
- `Multiplicity_rewrite/mapping_type_analysis.py`
  analyzes the combined head+tail relation-level CSV
- `Multiplicity_rewrite/mapping_type_plot.py`
  plots the combined head+tail analysis
- `Multiplicity_rewrite/mapping_type_side_analysis.py`
  analyzes the side-aware CSV
- `Multiplicity_rewrite/mapping_type_side_plot.py`
  plots the side-aware analysis

The original `Multiplicity_rewrite/main.py` remains the separate entry point for the overall link-prediction multiplicity experiment and is not used as the main thesis analysis script for mapping type.

## Output Structure

Current outputs are organized under:

```text
results/RotatE_FB15k237/
  link_prediction/
    multiplicity_num7_agg7_k10.csv
  mapping_type/
    combined/
      relation_metrics_num7_agg7_k10.csv
      support_summary.txt
      support_thresholds.csv
      grouped_stats.csv
      summary.txt
      boxplots.svg
    by_side/
      relation_metrics_num7_agg7_k10.csv
      grouped_stats.csv
      summary.txt
      boxplots.svg
```

This layout is intended to keep link-prediction reproduction results separate from thesis-specific mapping-type analysis.

## Relation-Level CSVs

### Combined CSV

The combined relation-level CSV is:

- `results/RotatE_FB15k237/mapping_type/combined/relation_metrics_num7_agg7_k10.csv`

This file aggregates head and tail query behavior together at the relation level.

### By-Side CSV

The side-aware relation-level CSV is:

- `results/RotatE_FB15k237/mapping_type/by_side/relation_metrics_num7_agg7_k10.csv`

Each row represents one:

- relation
- prediction side

with:

- `side = head` or `tail`

This format was introduced after observing that combined relation-level analysis can obscure directional mapping-type effects.

## Support Analysis

Support analysis was first performed on the combined relation-level CSV to decide an initial minimum-support threshold.

Current summary:

- total relations: `237`
- mapping-type counts:
  - `1-1`: `17`
  - `1-N`: `26`
  - `M-1`: `86`
  - `M-N`: `108`

Combined `test_support` distribution:

- min: `0`
- 25th percentile: `10`
- median: `23`
- 75th percentile: `77`
- 90th percentile: `224.2`
- max: `1447`

Candidate thresholds were compared, especially:

- `test_support >= 5`
- `test_support >= 10`

These two thresholds were retained because:

- `>= 5` removes very small relations while preserving broader coverage
- `>= 10` provides a stricter robustness check
- stronger thresholds such as `>= 20` reduce the number of `1-1` relations too aggressively

## First Combined Analysis

The first version of the analysis used combined relation-level metrics, meaning head and tail query behavior were merged into one value per relation.

That analysis produced only limited separation across mapping types.

This is an important negative result:

- the effect was not completely absent
- but it was not sharp enough to support a strong thesis claim if head and tail were kept merged

This led to the key methodological refinement of the current study:

> mapping type should be analyzed separately for head-side and tail-side prediction.

## Why the By-Side Analysis Matters

Mapping type is inherently directional.

For example:

- `1-N` means tail prediction is the structurally many side
- `M-1` means head prediction is the structurally many side

Therefore, if head and tail are combined, directional effects can cancel each other out.

This is exactly what happened in the first combined analysis.

The by-side analysis was introduced to test whether multiplicity follows this directional structure more clearly.

## Main By-Side Findings

The by-side analysis produces a much clearer pattern than the combined analysis.

### Head Side

For `head` prediction:

- `1-N` relations show the highest `hits_r` and the lowest `alpha_r` / `delta_r`
- `M-1` relations show the lowest `hits_r` and the highest `alpha_r` / `delta_r`

This is structurally coherent:

- in `1-N`, head prediction is the easier side
- in `M-1`, head prediction is the harder side

### Tail Side

For `tail` prediction:

- `M-1` relations show the highest `hits_r` and the lowest `alpha_r` / `delta_r`
- `1-N` relations show the lowest `hits_r` and the highest `alpha_r` / `delta_r`

This is again structurally coherent:

- in `M-1`, tail prediction is the easier side
- in `1-N`, tail prediction is the harder side

### Stable Interpretation Across Thresholds

The main directional pattern remains visible under both:

- `test_support >= 5`
- `test_support >= 10`

Thus, the observed trend is not just an artifact of a few tiny-support relations.

## What the Current Results Support

At the current stage, the results support the following thesis-level claim:

> The effect of mapping type on predictive multiplicity is strongly side-dependent.

More specifically:

- structurally harder directions tend to have lower `Hits@10`
- those same directions also tend to have higher multiplicity
- therefore, relation mapping structure is associated with both performance difficulty and disagreement instability

This is a stronger and more precise result than simply claiming that one mapping type is globally more multiplicity-prone than another.

## What the Current Results Do Not Support

The current experiment does not justify overly strong claims such as:

- mapping type is the only cause of multiplicity
- one mapping type is always the most unstable in every setting
- the result has already been validated across all models and datasets

At present, the result should be framed as:

- a strong directional pattern for `RotatE + FB15k-237`
- under the `without` repeated-run setting
- with relation-level analysis

## Recommended Thesis Wording

A safe wording for the current stage is:

> Predictive multiplicity is not uniformly distributed across relation structure.  
> When relation-level analysis is separated into head-side and tail-side prediction, the effect of mapping type becomes much clearer: structurally harder directions tend to be both less accurate and more multiplicity-prone.

## Immediate Next Step

This part of the experiment can be considered temporarily stabilized.

The next reasonable steps are:

1. write the current findings into thesis-style result paragraphs
2. decide whether to replicate the same workflow on `TransE`
3. later compare whether the same directional mapping-type pattern also appears across models
