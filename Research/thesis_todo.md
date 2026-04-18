# Thesis To-Do

## Current Overall Judgment

The current relation-pattern block is close to a stable stopping point.

At this stage, the most reasonable thesis structure is:

- `mapping type` as the main structural result
- `inverse` as an exploratory secondary result
- `symmetry` as a documented weak/negative result

This means the immediate priority is no longer to invent new relation patterns, but to:

1. complete the most valuable cross-model replications
2. freeze the current pattern-analysis block
3. then move to the next thesis component in a controlled way

## What Is Already Largely Completed

### Mapping Type

Current status:

- `RotatE + FB15k-237` result is stable
- by-side directional analysis is the real main result
- combined-only reading is no longer the preferred thesis presentation

Current thesis role:

- main positive result

### Inverse

Current status:

- first-round directional proxy has been recorded as too broad
- stricter v2 metrics have been implemented
- subgroup-oriented reading is now available
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

## Immediate Priorities

### 1. Add `TransE` Support To The Two More Important Pattern Lines

This is the most important remaining experiment block.

The current recommendation is:

- run `mapping type` on `TransE`
- run `inverse` on `TransE`

Reason:

- `mapping type` is the thesis main result and deserves at least one cross-model check
- `inverse` is still plausible enough to justify a model-comparison extension
- `symmetry` has already received its cross-model check and does not need further expansion now

### 2. Freeze The Relation-Pattern Block After Those Runs

Once the `TransE` supplements for `mapping type` and `inverse` are completed, the relation-pattern part should be considered experimentally closed for now.

That means:

- no new relation pattern should be opened at this stage
- no deeper symmetry digging should be added
- inverse should not receive another broad rerun unless a very specific writing need appears

### 3. Prepare The Transition To `relation frequency`

After the pattern block is frozen, the next content block should be:

- `relation frequency`

But this should begin only after the remaining `TransE` supplements are completed.

## Recommended Near-Term Experiment Plan

### A. `mapping type` on `TransE`

Goal:

- check whether the directional by-side mapping-type result also appears in `TransE`

Minimum required outputs:

- relation-level by-side multiplicity table
- `mapping_type` summary
- direct comparison against current `RotatE` findings

Main question:

- does the harder side under each mapping regime still show lower `Hits@10` and higher `alpha/delta`?

This is higher priority than all other remaining pattern experiments.

### B. `inverse` on `TransE`

Goal:

- check whether the current inverse story remains exploratory under another model

Recommended scope:

- preserve the existing `v1` / `v2` distinction
- at minimum, run the stricter `v2` analysis
- if the implementation cost is low, keep the `v1` baseline as well for completeness

Main question:

- does `TransE` make the inverse-like subgroup cleaner, noisier, or essentially unchanged?

This matters less than `mapping type`, but still enough to justify one model-comparison pass.

## Topics To Defer Until After The Pattern Block

### `relation frequency`

This is the next serious content block after the relation-pattern experiments.

Current judgment:

- it fits the thesis direction better than `entity frequency`
- it should be integrated into the current relation-level framing rather than copied mechanically from the original paper

Recommended policy:

- do **not** start detailed integration yet
- first finish the remaining `TransE` work for `mapping type` and `inverse`
- then discuss how `relation frequency` should connect to the existing thesis story

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

- this branch is real but secondary
- most of the core experimentation is already done
- remaining work is mainly parameter consolidation and final presentation

Recommended status:

- postpone until the main thesis analysis block is better frozen

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

These are better handled after the remaining high-value experiments are finished.

## Current Recommended Order

1. run `mapping type` on `TransE`
2. run `inverse` on `TransE`
3. update experiment notes and freeze the relation-pattern block
4. design how `relation frequency` should be integrated into the thesis
5. later return to the efficiency branch and parameter consolidation

## Current Non-Goals

At the current stage, the following should **not** be expanded further:

- new relation patterns beyond the current three
- more symmetry refinements
- entity-frequency main-line analysis
- broad multi-model expansion beyond the most valuable `TransE` checks

## One-Sentence Working Summary

The current thesis work should now move from “opening more pattern ideas” to “closing the relation-pattern block cleanly with the most valuable `TransE` supplements, then transitioning to `relation frequency`.”
