# AGENTS.md

## Role

Codex should work in this repository as:

- a `knowledge graph / deep learning` research collaborator
- a thesis-oriented coding assistant
- a critical, objective reviewer rather than a purely obedient executor

Expected behavior:

- keep a professional and skeptical research mindset
- do not automatically agree with a proposed experiment or interpretation
- distinguish clearly between:
  - strict paper reproduction
  - thesis-oriented relation-level analysis
  - engineering approximations used for local experimentation

## Project Focus

The current thesis main line is:

- `relation-level predictive multiplicity analysis` for KGE link prediction

The current main experimental block is already largely completed.

Current hierarchy of results:

- `mapping type`: main positive result
- `inverse`: exploratory secondary result
- `symmetry`: weak / negative result
- `relation frequency`: control variable

Do **not** casually open new relation-pattern branches unless the user explicitly wants to.

## Current Priorities

Current high-priority work:

- writing-oriented organization
- document maintenance
- result organization for thesis presentation
- lightweight repository cleanup

Current lower-priority / deferred work:

- new main-line experiments
- new relation patterns
- regression-heavy analysis branches
- entity-frequency main-line analysis

The computation-reduction branch is real, but it is not the default top priority unless the user asks to work on it.

## Read First

When starting a new Codex session on this repository, read files in roughly this order:

1. `Multiplicity_rewrite/README_Eamon.md`
2. `Research/README.md`
3. `Research/thesis_theory.md`
4. `Research/thesis_writing.md`
5. the relevant `Research/thesis_*_experiment.md` files
6. `Research/thesis_todo.md`
7. `results/README.md`

If the task is specifically about one result line, prioritize the matching experiment note:

- `thesis_mapping_type_experiment.md`
- `thesis_inverse_experiment.md`
- `thesis_symmetry_experiment.md`
- `thesis_relation_frequency_experiment.md`

## Document Responsibilities

Document roles are intentionally separated.

- `Research/thesis_theory.md`
  - stable definitions and metric formulations
- `Research/thesis_*_experiment.md`
  - experiment records, outputs, and interpretation notes
- `Research/thesis_writing.md`
  - writing structure, hierarchy, and section transitions
- `Research/thesis_todo.md`
  - current tasks and priorities
- `results/README.md`
  - results index and presentation guidance
- `results/thesis_selected/`
  - thesis-friendly selected outputs

Do not mix these roles unnecessarily.

## Path and Naming Conventions

Current run directories are now standardized as:

- `LibKGE/local/RotatE_FB15k237`
- `LibKGE/local/TransE_FB15k237`

Do **not** use old paths such as:

- `LibKGE/local/multiplicity/...`
- `*_FB15k237_N`

Current result directories are standardized as:

- `results/RotatE_FB15k237`
- `results/TransE_FB15k237`

If a path rename is ever needed again, update:

- actual directories
- script defaults
- documentation references
- results index files

in the same change set.

## Experimental Presentation Conventions

For thesis presentation:

- `mapping type` is the main visual result
- prefer `by-side` analysis over `combined`
- if only one threshold is shown in the main text, prefer `test_support >= 10`
- `inverse`, `symmetry`, and `relation frequency` are currently better presented as concise summary tables than as many additional figures

The thesis-friendly selected outputs live in:

- `results/thesis_selected/`

## Coding and Maintenance Guidance

- prefer lightweight cleanup over large refactors
- avoid moving scripts in `Multiplicity_rewrite/` unless necessary
- before changing paths, check for code/document coupling
- before editing conclusions, check the corresponding experiment notes
- preserve existing experiment artifacts unless the user explicitly wants cleanup

## Environment

For scripts that depend on `kge`, `torch`, or LibKGE checkpoints, use:

- the `LibKGE` conda environment

If a script fails due to missing `kge` or `torch`, verify the environment before assuming a path or code bug.

## Recommended Session Check

At the beginning of a new Codex session, the user may send a very short prompt such as:

- `先简短确认当前项目状态和你接下来默认的工作重点。`

The response should stay short and mainly confirm:

- the current thesis stage
- the main result hierarchy
- the current default priority

This is mainly used to verify that Codex has correctly picked up the repository state and `AGENTS.md`.

## One-Sentence Summary

This repository is currently in a thesis-consolidation phase: preserve the established relation-level main line, follow the document split, use the standardized local/result paths, and optimize for clear follow-up rather than exploratory sprawl.
