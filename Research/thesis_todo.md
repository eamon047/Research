# Thesis To-Do

## Current Overall Judgment

The current thesis main-line experiment block is now closed on the experimental
side.

At this stage, the most reasonable thesis structure is:

- `mapping type` as the main structural result
- `inverse` as an exploratory secondary result
- `symmetry` as a documented weak/negative result
- `relation frequency` as a support / sparsity control variable

This means the immediate priority is no longer to invent new relation-level
experiments. The remaining work for this block is writing and presentation,
not new analysis design:

1. keep the current main-line block frozen
2. preserve the current result hierarchy
3. postpone figure polishing and full chapter drafting until the user chooses to
   write the thesis sections together
4. move to the computation-reduction / model-pool side branch as the next
   experimental component

## Main-Line Experiment Closure Decision

The relation-level predictive multiplicity block can now be treated as
experimentally complete.

Closed components:

- `mapping type`
- `inverse`
- `symmetry`
- `relation frequency`

Closure conditions already satisfied:

- core results exist for both `RotatE` and `TransE`
- selected thesis-friendly summaries have been created
- result files are indexed under `results/README.md`
- key terms and fields are consolidated in `thesis_theory.md`
- outdated path and status notes have been cleaned up
- no further metric redesign or full five-repeat retraining is recommended

Allowed future work on this block:

- wording fixes
- figure polishing
- table formatting
- small consistency corrections
- appendix-level robustness only if a concrete writing or defense need appears

Disallowed as default next steps:

- new relation patterns
- further inverse / symmetry metric redesign
- broad regression-heavy control analysis
- new full model retraining solely for mean/std reporting

## Current Decision On Further Metric Redefinition

The current recommendation is **not** to continue redefining the weaker
relation-level factors as a new main experimental round.

Reason:

- `inverse` has already received a stricter v2 metric family and a cross-model
  check; its remaining contribution is subgroup-oriented rather than global
- `symmetry` has already received the necessary self-loop correction and a
  cross-model check; the result remains weak and structurally concentrated
- further redefinitions would likely expand the scope faster than they improve
  the central thesis argument

The more thesis-safe direction is:

- close the current main-line block
- perform writing-oriented gap checking
- only add small supplementary analyses if a concrete thesis-writing gap
  appears

This decision does not forbid future appendix-level checks. It means that new
metric redesign should not be treated as the default next step for the main
thesis line.

## Current Decision On Five-Repeat Retraining

The current recommendation is **not** to run a new full five-repeat retraining
protocol solely to report mean and standard deviation.

Reason:

- the common "repeat five times and report mean +/- std" protocol is mainly
  used to show that a model-performance number is not a seed accident
- in this thesis, repeated-run variation is itself part of the research object:
  predictive multiplicity is measured from disagreement across trained runs
- the current main results already use a model pool of repeated seeds rather
  than a single training run
- the main positive result has also been checked across `RotatE` and `TransE`
  and across support thresholds
- retraining five complete experimental pools would be expensive while adding
  limited evidence to the current relation-level thesis claim

The more appropriate robustness option, if a writing or defense need appears,
is a lightweight model-pool subsampling check:

- repeatedly sample smaller subsets from the existing seed pool
- recompute the core mapping-type by-side summary
- verify whether the key directional ordering remains stable
- report this explicitly as pool-subsampling robustness, not as a fresh
  five-repeat retraining protocol

This also connects naturally to the later computation-reduction branch, where
the question is how much of the original model pool is needed to recover the
same qualitative conclusions.

## What Is Already Largely Completed

### Mapping Type

Current status:

- `RotatE + FB15k-237` result is stable
- `TransE + FB15k-237` replication completed
- by-side directional analysis is the real main result
- combined-only reading is no longer the preferred thesis presentation

Current thesis role:

- main positive result

### Inverse

Current status:

- first-round directional proxy has been recorded as too broad
- stricter v2 metrics have been implemented
- subgroup-oriented reading is now available
- `TransE` comparison completed
- global monotonic claim is not supported

Current thesis role:

- exploratory secondary line
- possible limited positive subgroup observation

### Symmetry

Current status:

- `RotatE` baseline completed
- self-loop caveat documented
- excluding-self v2 analysis completed
- `TransE` comparison completed
- cross-model result still weak

Current thesis role:

- weak / negative result

### Relation Frequency

Current status:

- `RotatE` base analysis completed
- `mapping type × frequency` by-side analysis completed
- `TransE` comparison completed
- the original paper’s simple negative frequency trend is not reproduced under the current thesis setting
- the control-variable conclusion is usable

Current thesis role:

- support / sparsity control variable
- useful mainly for defending the independence of the mapping-type result

## Immediate Priorities

### 1. Freeze The Main-Line Experiment Block

This includes:

- `mapping type`
- `inverse`
- `symmetry`
- `relation frequency`

The current recommendation is:

- do not open new relation patterns
- do not rerun the existing lines unless a specific writing need appears
- treat the experimental block as complete enough for thesis writing

### 2. Shift To Writing-Oriented Consolidation

The next valuable work is:

- unify the thesis wording across experiment notes
- decide which figures are worth keeping
- convert the current results into compact result-section logic

### 3. Move To The Efficiency Branch

The computation-reduction / model-pool branch is now the next experimental
component to inspect.

The branch should be positioned as a secondary method / efficiency analysis,
not as a replacement for the relation-level structural findings.

## Recommended Near-Term Work

### A. Consolidate The Main Experimental Story

Goal:

- turn the current experiment block into a stable thesis narrative

Key tasks:

- align the wording across `mapping type`, `inverse`, `symmetry`, and `relation frequency`
- keep the hierarchy clear:
  - `mapping type` main result
  - `inverse` exploratory secondary result
  - `symmetry` weak / negative result
  - `relation frequency` support-level control variable

### B. Decide Which Figures Are Necessary

Goal:

- keep only the most thesis-useful visuals

Current likely priorities:

- `mapping type` by-side figure
- `TransE` by-side figure for mapping type
- optionally one `relation frequency × mapping type` figure if it materially helps the control-variable argument

## Topics To Defer Until After The Pattern Block

### `relation frequency`

This block is no longer pending; it has already been integrated into the main line.

Current judgment:

- it fits the thesis direction better than `entity frequency`
- it should be integrated into the current relation-level framing rather than copied mechanically from the original paper

Recommended policy:

- keep it as a control-variable section
- do not inflate it into a fourth pattern section
- do not force reproduction of the original paper’s negative trend when the current thesis setting does not support it

### `entity frequency`

Current judgment:

- remove it from the main thesis plan

Reason:

- it does not match the current relation-centered thesis framing as naturally as `relation frequency`
- adding it now would likely expand the scope without improving the main argument enough

Recommended status:

- dropped from the main line
- only mentionable later as related-work context if needed

### Efficiency / Reduced Computation Branch

Current judgment:

- this branch is real and can now be inspected
- it should remain secondary to the relation-level main result
- its likely role is to ask how much of the original model pool is needed to
  recover similar multiplicity or voting conclusions

Recommended status:

- start with code and artifact inspection
- clarify the exact optimization question before running new experiments
- avoid letting this branch reopen the relation-pattern analysis

## Writing-Oriented To-Dos

These should begin in parallel only lightly, not as the main focus yet.

### Short-Term Writing Prep

- maintain experiment notes cleanly after each new `TransE` run
- keep theory definitions stable and avoid introducing new metric families casually
- gradually convert stable conclusions into thesis-safe wording

### Not Yet The Main Focus

- full thesis prose drafting
- large-scale result section polishing
- heavy figure production

These are better handled after the computation-reduction branch is scoped.

## Current Recommended Order

1. keep the main-line experiment block frozen
2. inspect the computation-reduction / model-pool branch
3. decide whether a small experiment is needed there
4. later return to figure polishing and thesis prose drafting as one writing pass

## Current Non-Goals

At the current stage, the following should **not** be expanded further:

- new relation patterns beyond the current three
- more symmetry refinements
- entity-frequency main-line analysis
- broad multi-model expansion beyond the current `RotatE / TransE` coverage
- new frequency-modeling variants such as regression-heavy branches

## One-Sentence Working Summary

The relation-level main-line experiment block is closed; the next experimental
work should inspect the computation-reduction / model-pool branch without
reopening the relation-pattern analysis.
