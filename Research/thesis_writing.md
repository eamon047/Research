# Thesis Writing Notes

## Scope of This File

This file is **not** the full thesis outline.

At the current stage, it only records the agreed writing structure for the
**main experimental block**, together with the role of each result and the
transition logic between sections.

The full thesis framework should be decided later, after:

- checking reference graduate theses
- clarifying school-specific format expectations
- deciding how to place the computation-reduction side branch

## Role of This File vs Other Files

- `thesis_theory.md`
  - stable definitions and metric formulations
- `thesis_*_experiment.md`
  - experiment process, results, and interpretation notes
- `thesis_todo.md`
  - task management and next-step planning
- `thesis_writing.md`
  - writing-oriented structure, hierarchy, and section transitions

Current policy:

- do not keep expanding writing structure inside `theory`
- do not mix chapter-level writing decisions into experiment logs
- use this file as the single place for writing organization notes

## Current Writing Judgment

The current main experimental block should **not** be written as four equal
pattern sections.

The stable hierarchy is:

- `mapping type` as the main structural result
- `inverse` as an exploratory secondary result
- `symmetry` as a weak / negative result
- `relation frequency` as a control-variable analysis

This hierarchy should remain visible throughout the writing.

## Candidate-Factor Framing

The four factor families in the main experimental block should **not** be
introduced as pre-validated laws.

The recommended framing is:

- `mapping type` as a natural candidate explanatory factor
- `inverse-like support` as a plausible structural candidate
- `symmetry` as another plausible structural candidate
- `relation frequency` as a support / sparsity control variable

In other words, the thesis should present these factors as:

> candidate explanatory factors to be tested under the current thesis setting

rather than as structural rules that are assumed to hold in advance.

This is important because the final contribution is not:

- that every intuitive factor is confirmed

but rather:

- that the thesis distinguishes which relation-level candidate factors remain
  explanatory after empirical testing, and which do not

## Why These Factors Were Chosen

The current writing should make clear that these factors were not chosen
arbitrarily.

Recommended high-level motivation:

- `mapping type`
  - it directly captures directional connectivity structure
  - it is naturally aligned with head-side and tail-side prediction difficulty
- `inverse-like support`
  - it captures whether a relation has plausible reverse structural support in
    the training graph
- `symmetry`
  - it captures whether a relation shows within-relation bidirectional support
- `relation frequency`
  - it provides a simple support / sparsity axis and acts as a control variable

However, these motivations should be described as:

- reasons that make the factors worth testing

not as:

- guarantees that the resulting empirical relation must be strong or clean

## Interpreting Mixed Outcomes

The chapter should not be written as a story of:

- “one factor was guessed correctly, two were guessed incorrectly”

The better framing is:

- several motivated candidate factors were tested
- these factors ended up with different explanatory status under the current
  operationalization

The current status should be written explicitly as:

- `mapping type`: stable explanatory factor
- `inverse`: conditional or subgroup-based factor
- `symmetry`: not supported as a standalone explanatory factor
- `relation frequency`: control axis

This turns the contribution into a filtering result:

> the thesis identifies which relation-level intuitions survive empirical
> scrutiny under the current operationalization of predictive multiplicity

instead of a yes/no scorecard on initial intuition.

## Main Experimental Block: Draft Structure

### X. Relation-Level Structural Analysis of Predictive Multiplicity

This chapter should serve as the unified entry point for the main experiments.

Its function is to state that:

- the object of analysis is `relation-level predictive multiplicity`
- the goal is to study how relation-level factors relate to multiplicity
- the factor families are introduced as candidate explanatory factors rather
  than pre-validated laws
- metric definitions, datasets, models, and repeated-run settings have already
  been introduced earlier and are not redefined in full here

### X.1 Mapping Type Analysis

This is the main result section and should receive the largest weight.

Suggested internal structure:

- `X.1.1 Combined Relation-Level Results`
  - briefly introduce the combined view
  - note that it is not sufficiently clean for the main conclusion
- `X.1.2 By-Side Relation-Level Results`
  - present the head-side and tail-side directional results
  - treat this as the real core finding
- `X.1.3 Cross-Model Comparison: RotatE and TransE`
  - show that the by-side pattern is replicated across models
- `X.1.4 Interim Summary of Mapping Type`
  - conclude that `mapping type` is the strongest structural factor in the thesis
  - emphasize that the effect must be analyzed by side rather than only in the
    combined view

### X.2 Inverse-Like Structural Analysis

This section should be clearly lighter than `mapping type`.

Important writing policy:

- the formal main analysis should use the stricter `v2` inverse-like metrics
- the naive directional proxy should still be mentioned briefly as motivation
- `v1` does not need to be written as a separate equal-weight result section

Suggested internal structure:

- `X.2.1 Motivation for a Stricter Inverse-Like Definition`
  - briefly explain why a naive directional proxy is too broad
  - state that it mixes in reverse containment / reverse overlap
- `X.2.2 Inverse-Like Metrics Used in This Thesis`
  - refer back to the earlier definition section
  - state that the main analysis uses `mutual_inverse_strength` and
    `inverse_clarity`
- `X.2.3 Empirical Results and High-Confidence Subgroup`
  - state clearly that no global monotonic law is supported
  - explain that a high-confidence subgroup still exists
- `X.2.4 Cross-Model Comparison: RotatE and TransE`
  - show the subgroup-oriented pattern is not model-specific
- `X.2.5 Interim Summary of Inverse`
  - conclude that inverse is not a global main result
  - retain it as a limited subgroup-based observation

### X.3 Symmetry Analysis

This should be a relatively short section.

Suggested internal structure:

- `X.3.1 Operational Definition and Self-Loop Handling`
  - briefly recall the symmetry definition
  - explain that self-loops artificially inflate raw symmetry
  - state that the main analysis uses the excluding-self version
- `X.3.2 Empirical Results`
  - note the sparse and highly skewed distribution
  - state that no stable positive relation with multiplicity is found
- `X.3.3 Cross-Model Comparison: RotatE and TransE`
  - show the weak result is not model-specific
- `X.3.4 Interim Summary of Symmetry`
  - conclude that symmetry is not a useful main explanatory factor under the
    current thesis setting

### X.4 Relation Frequency as a Control Variable

This section should **not** be framed as another pattern section.

Its writing role is to act as a control analysis.

Suggested internal structure:

- `X.4.1 Motivation and Definition`
  - explain that relation frequency comes from training-graph support
  - state explicitly that it is a control variable rather than a fourth pattern
- `X.4.2 Base Relation-Level Frequency Results`
  - report that the original paper's simple negative trend is not directly
    reproduced under the current thesis setting
  - explain briefly that the statistical scope differs from the original pooled
    analysis
- `X.4.3 Frequency-Stratified Mapping Type Analysis`
  - present the key result of this section
  - show that the by-side mapping-type effect remains after frequency
    stratification
- `X.4.4 Interim Summary of Relation Frequency`
  - conclude that relation frequency is better treated as a control variable
  - state that `mapping type` is not merely a frequency artifact

### X.5 Chapter Discussion

This section should unify the main experimental block before the thesis moves on
to later chapters.

Its job is to make the hierarchy explicit:

- `mapping type` is the main result
- `inverse` is an exploratory secondary result
- `symmetry` is a weak / negative result
- `relation frequency` is a control-variable analysis

It should also make one higher-level point explicit:

- a plausible structural intuition does not automatically become a stable
  explanatory factor
- whether it survives depends on how cleanly it is operationalized
- whether it retains enough independent variation after cleaning
- whether it is confounded with or interacts with other structural regimes

## Definition Placement Policy

The mathematical definitions of these factors should **not** be fully expanded
inside the main results chapter.

Recommended policy:

- put the formal definitions in the earlier theory / methodology chapter
- in the main experimental chapter, only give a short reminder of which
  definition is being used

This applies to:

- `mapping type`
- `inverse-like metrics`
- `symmetry score`
- `relation frequency`

## Specific Policy for Inverse vs Symmetry

These two sections should not be written using the same narrative.

### Inverse

Recommended treatment:

- mention the limitation of the naive directional proxy briefly
- adopt the stricter `v2` family as the formal main analysis
- keep the detailed `v1` record in experiment notes or appendix-style material

This is a **redefinition / refinement** issue, not a simple data-cleaning issue.

### Symmetry

Recommended treatment:

- directly explain the self-loop caveat
- state that raw symmetry is unsuitable as the main operational measure
- use the excluding-self version in the formal main analysis

This is a **metric-cleaning** issue and can be written more directly.

## Weighting Inside the Main Experimental Block

Recommended relative emphasis:

- `mapping type`: heaviest
- `inverse`: medium
- `symmetry`: light
- `relation frequency`: medium-light but methodologically important
- `chapter discussion`: short but explicit

## Transition Logic Between Sections

The current preferred order is:

1. `mapping type`
2. `inverse`
3. `symmetry`
4. `relation frequency`
5. chapter discussion

Reasoning:

- start from the strongest and most stable structural finding
- then move to a weaker but still informative structural factor
- then present a clearly weak / negative pattern
- then close with a control-variable analysis

This produces a natural progression from:

- main positive result
- to exploratory secondary result
- to weak / negative result
- to control-based consolidation

## Current Non-Goals for This File

This file should **not** yet decide:

- the full thesis chapter plan
- the placement of background / related work / model introduction chapters
- the final position of the computation-reduction branch
- the exact prose wording of each subsection
- final figure numbering or final table numbering

Those decisions belong to a later writing stage.

## Current One-Sentence Summary

At the writing-structure level, the main experimental block should be organized
around `mapping type` as the core result, with `inverse` as a limited secondary
result, `symmetry` as a weak/negative result, and `relation frequency` as a
control-variable analysis.
