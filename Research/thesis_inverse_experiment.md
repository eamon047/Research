# Thesis Inverse Experiment

## Purpose of This Note

This note records the experimental setup, code path, output files, and current findings for the inverse-family analysis under the thesis main line.

At the current stage, this document has moved beyond pure planning. It now serves as a maintained record of:

- the original directional inverse baseline
- the stricter `v2` inverse-like metrics
- the resulting subgroup-oriented interpretation
- the `RotatE / TransE` comparison

## Current Scope

The current inverse-family study follows the same narrow thesis setup used in the mapping-type study:

- models: `RotatE`, `TransE`
- dataset: `FB15k-237`
- evaluation setting: `without`
- analysis unit: `relation-level`

The key thesis-side structural variables are:

- `mutual_inverse_strength`
- `inverse_clarity`

The current goal is not to discover every inverse pair in the graph as an end in itself. The goal is to test whether inverse-like structural support is associated with predictive multiplicity.

The directional `v1` proxy is retained in this note as a baseline and audit trail, but it is no longer the preferred formal thesis definition.

## Main Working Hypothesis

The current first-round hypothesis is:

> stronger inverse structural support is associated with lower predictive multiplicity severity.

In practical terms, this means relations with clearer inverse evidence in the training graph may show:

- lower `alpha`
- lower `delta`
- possibly higher `Hits@10`

The first two are the primary focus. `Hits@10` is a useful auxiliary result, but not the main target of this section.

## Current Positioning Update

After the first merged analysis and the subsequent metric audit, the inverse-family section should no longer be framed as a likely main positive result.

At the current stage, the safer positioning is:

- `mapping type` remains the stable main thesis result
- `inverse` should be treated as an exploratory secondary line
- if the signal can be cleaned up with a stricter metric, it may still become a useful supporting subsection
- if the signal remains unstable, this section should be written as a negative or failure-analysis result rather than forced into a positive claim

This update is important for scope control. The inverse line is still worth continuing, but it should not be allowed to destabilize the main thesis story.

## Analysis Logic

The inverse-family analysis has two conceptual layers:

1. pair-level inverse evidence
2. relation-level inverse strength

The final thesis analysis remains relation-level. Therefore:

- relation pairs are only an intermediate step
- the final analysis table still has one row per relation

## Implemented Structural Statistics

The first implementation now outputs a relation-level inverse statistics table with:

- `relation_id`
- `relation_name`
- `train_support`
- `inverse_strength`
- `best_inverse_partner_id`
- `best_inverse_partner_name`
- `best_inverse_score`
- `best_inverse_overlap_count`

At the current stage:

- `inverse_strength` and `best_inverse_score` are numerically the same
- both are still kept for readability
- `best_inverse_overlap_count` is retained because a high score on very small support can otherwise be misleading

In addition, a pair-level auxiliary table is also exported with:

- `source_relation_id`
- `source_relation_name`
- `target_relation_id`
- `target_relation_name`
- `source_train_support`
- `target_train_support`
- `overlap_count`
- `inverse_score`

This pair-level table is not the main thesis analysis table, but it is useful for sanity checks and later case studies.

## Planned Merge With Multiplicity Results

After inverse statistics are computed, they will be joined with the existing relation-level multiplicity outputs.

The initial merge target should be the combined relation-level multiplicity table, not the side-aware version.

Reason:

- inverse strength already comes from a directional pair-level definition
- the first inverse experiment should first establish whether a usable signal exists at the overall relation level
- side-aware refinement can be considered later if necessary

## Planned Result Variables

The first merged analysis table is expected to contain at least:

- `relation_id`
- `relation_name`
- `inverse_strength`
- `best_inverse_partner`
- `hits_r`
- `alpha_r`
- `delta_r`
- `test_support`

Later enhancements may also include:

- `mapping_type`
- `frequency`
- other relation-pattern variables

But these are not required for the first run.

## Planned Analysis Steps

The current recommended execution order is:

1. compute relation-level inverse statistics from the training graph
2. run sanity checks on the inverse table
3. merge inverse statistics with relation-level multiplicity outputs
4. perform correlation analysis
5. perform bucket-based analysis

This first round should avoid expanding into too many robustness checks before the basic signal is confirmed.

## Planned Sanity Checks

Before any multiplicity analysis, the inverse statistics table should be checked for:

- whether `inverse_strength` is overly concentrated near zero
- whether the top `best_inverse_partner` relations look semantically plausible
- whether a small number of relations dominate the score distribution
- whether the score distribution has enough spread for downstream analysis

This step is important because inverse definitions can be mathematically reasonable but empirically uninformative if the resulting distribution is too degenerate.

## Planned Statistical Analysis

The first analysis round should remain simple and interpretable.

### Correlation

Recommended first-round correlations:

- `inverse_strength` vs `alpha_r`
- `inverse_strength` vs `delta_r`
- `inverse_strength` vs `hits_r`

Spearman correlation is the preferred default.

### Bucket Analysis

Recommended next step:

- bucket `inverse_strength`
- compare average `alpha_r`
- compare average `delta_r`
- compare average `hits_r`

This is likely to be more interpretable for thesis writing than relying only on raw scatter plots.

## Planned Figures

The first round should likely include:

1. `inverse_strength` vs `alpha_r`
2. `inverse_strength` vs `delta_r`
3. optional: `inverse_strength` vs `hits_r`
4. bucket-based mean plots

At the current stage, no plotting choices are frozen yet.

## Code Status

The inverse-family code is implemented in `Multiplicity_rewrite/` using the same general style as the mapping-type scripts.

Currently implemented:

- `inverse_relation_stats.py`
  computes inverse statistics from training triples
- `inverse_analysis.py`
  merges inverse statistics with relation-level multiplicity outputs and computes grouped summaries
- `inverse_mapping_interaction_analysis.py`
  analyzes inverse-strength effects within each mapping type

Still planned:

- `inverse_plot.py`
  generates visualizations

The preferred principle remains:

- keep inverse analysis independent from `main.py`
- keep thesis-specific analysis scripts easy to rerun and maintain

## Current Status

Current status:

- theory and experimental framing have been discussed
- the first inverse-statistics extraction script has been implemented
- the first inverse CSVs have been generated
- sanity checking of inverse-score distribution has been completed
- inverse-to-multiplicity merge analysis has been completed

Therefore, this section is currently at the “first merged inverse-vs-multiplicity analysis completed” stage.

## Current Outputs

Current outputs are stored under:

- `results/RotatE_FB15k237/inverse/`

The current files are:

- `relation_inverse_stats.csv`
- `relation_inverse_pair_scores.csv`
- `relation_inverse_multiplicity_merged.csv`
- `correlation_stats.csv`
- `bucket_stats.csv`
- `analysis_summary.txt`

## Current Sanity-Check Summary

The first sanity check indicates that the inverse-strength definition is empirically usable on `FB15k-237`.

### Table Shape

- relation-level rows: `237`
- pair-level rows: `55932 = 237 * 236`

This confirms that every relation was compared against every other relation.

### Distribution of `inverse_strength`

Current summary:

- min: `0.0`
- 25th percentile: `0.0`
- median: `0.0116`
- 75th percentile: `0.3193`
- 90th percentile: `0.6861`
- max: `0.8794`

Additional counts:

- `inverse_strength = 0`: `97` relations
- `inverse_strength >= 0.5`: `34` relations
- `inverse_strength >= 0.8`: `12` relations

Interpretation:

- the variable is not degenerate
- it is not collapsing to all zeros
- it also shows enough spread to support downstream correlation and bucket analysis

### Qualitative Plausibility

The top-scoring relation pairs appear structurally plausible in the training graph.

Examples include relations involving:

- administrative containment
- educational institution / campus reversal
- sports roster / team / position structures

These are not always “perfect semantic inverses” in a human-labeled sense, but they do behave like strong reverse-support partners under the current training-graph definition. This is acceptable because the current feature is intended to capture structural inverse support, not only textbook semantic inverse pairs.

## Current Known Caveat

One known presentation issue remains:

- when `inverse_strength = 0`, the current script still assigns a `best_inverse_partner`

This happens because all candidate scores are tied at zero, and the current implementation resolves the tie by relation id.

This does not affect the usefulness of `inverse_strength` itself, but it can make `best_inverse_partner` misleading for zero-strength relations.

Therefore, a later cleanup should set:

- `best_inverse_partner_id`
- `best_inverse_partner_name`

to empty values when `best_inverse_score == 0`.

## First Merge Analysis Summary

The first merge analysis uses:

- inverse table: `relation_inverse_stats.csv`
- multiplicity table: `results/RotatE_FB15k237/mapping_type/combined/relation_metrics_num7_agg7_k10.csv`
- merged table: `relation_inverse_multiplicity_merged.csv`

The first analysis reports:

- Spearman correlations
- bucket-based summaries

for three support settings:

- all relations
- `test_support >= 5`
- `test_support >= 10`

### Correlation Results

The first-round Spearman results do not support a simple monotonic version of the original hypothesis.

For `test_support >= 5`:

- `inverse_strength` vs `hits_r`: `-0.2609`
- `inverse_strength` vs `alpha_r`: `0.2579`
- `inverse_strength` vs `delta_r`: `0.2732`

For `test_support >= 10`:

- `inverse_strength` vs `hits_r`: `-0.2835`
- `inverse_strength` vs `alpha_r`: `0.2249`
- `inverse_strength` vs `delta_r`: `0.2383`

Taken at face value, these coefficients suggest that inverse strength is not simply associated with lower multiplicity under the current combined relation-level setting.

### Bucket Results

The bucket analysis suggests a more nuanced pattern.

Relations with `inverse_strength = 0` and relations with very strong inverse support (`> 0.5`) both show:

- relatively high `Hits@10`
- relatively low `alpha`
- relatively low `delta`

By contrast, the intermediate inverse-strength buckets show:

- lower `Hits@10`
- higher `alpha`
- higher `delta`

For example, under `test_support >= 10`:

- `zero` bucket:
  - `hits_mean = 0.6700`
  - `alpha_mean = 0.1721`
  - `delta_mean = 0.1031`
- `(0.5, 1.0]` bucket:
  - `hits_mean = 0.6193`
  - `alpha_mean = 0.1182`
  - `delta_mean = 0.0738`
- `(0, 0.1]` bucket:
  - `hits_mean = 0.4965`
  - `alpha_mean = 0.3314`
  - `delta_mean = 0.1882`

This means the current signal appears more non-monotonic than linearly negative.

### Current Interpretation

At the current stage, the safest interpretation is:

- inverse strength is not an obviously useless variable
- but its relationship to multiplicity is not well described by a simple “more inverse support means less multiplicity” rule
- the current combined relation-level setting may be mixing together multiple structural subcases

This means the inverse-family section remains viable, but it currently points toward a more nuanced structural story than the original first-round hypothesis.

## Immediate Next Step

The immediate next step should be one of the following:

1. visualize the merged results with scatter plots and bucket plots
2. inspect whether `mapping_type` or other relation structure is interacting with inverse strength
3. consider whether a side-aware inverse follow-up is necessary if the combined relation-level signal remains difficult to interpret

## Mapping-Type Interaction Follow-up

The next follow-up has now also been completed.

This analysis uses:

- input: `relation_inverse_multiplicity_merged.csv`
- script: `Multiplicity_rewrite/inverse_mapping_interaction_analysis.py`
- output directory: `results/RotatE_FB15k237/inverse/mapping_interaction/`

The current outputs are:

- `correlation_by_mapping_type.csv`
- `bucket_stats_by_mapping_type.csv`
- `summary.txt`

### Main Observation

The interaction analysis suggests that the inverse signal is not uniform across mapping types.

For `test_support >= 5`:

- `1-N`:
  - `inverse_strength` vs `alpha_r`: `0.4462`
  - `inverse_strength` vs `delta_r`: `0.4689`
- `M-1`:
  - `inverse_strength` vs `alpha_r`: `0.4563`
  - `inverse_strength` vs `delta_r`: `0.4723`
- `M-N`:
  - `inverse_strength` vs `alpha_r`: `0.1321`
  - `inverse_strength` vs `delta_r`: `0.1405`

The `1-1` group shows the opposite direction, but the sample size is too small to support a strong claim.

### Current Interpretation After Interaction Analysis

The combined inverse analysis was not simply noisy. Instead, it appears to be mixing together different structural regimes.

At the current stage, the safest interpretation is:

- the inverse effect depends on mapping structure
- in `1-N` and `M-1`, higher inverse strength is associated with higher multiplicity under the current combined relation-level setting
- in `M-N`, the same association is much weaker
- the `1-1` group remains too small for strong interpretation

This means the inverse-family section remains meaningful, but its interpretation should now explicitly acknowledge interaction with mapping type.

## Metric Audit After the First Round

After inspecting the merged outputs more closely, the main problem appears not to be a coding bug but the definition of the current metric itself.

### What the Current Metric Actually Measures

The current `inverse_strength` is a directional overlap score:

```math
s(r_1 \to r_2) = \frac{|E_{r_1} \cap E_{r_2}^{rev}|}{|E_{r_1}|}
```

and for each relation `r`, the exported relation-level score is:

```math
\operatorname{InvStrength}(r) = \max_{r' \neq r} s(r \to r')
```

This is mathematically valid, but empirically it behaves more like a one-sided reverse-coverage or recall-style score than a strict inverse indicator.

### Why This Can Be Misleading

This directional definition can assign a high score even when:

- `r_1` is only a narrower subset of `r_2^{rev}`
- `r_2` is a much broader or more generic relation
- the pair is better described as reverse containment than as a clean inverse relation

In those cases:

- `s(r_1 \to r_2)` can be very high
- but `s(r_2 \to r_1)` can remain very low

So a high first-round `inverse_strength` does not necessarily mean that the relation has a strong mutual inverse partner.

### Concrete Audit Result

Manual inspection of high-scoring pairs confirms that the first-round metric mixes at least two different structural cases:

- genuinely strong inverse-like pairs with substantial mutual overlap
- one-sided reverse-containment pairs where only the narrower side receives a high score

For example, some high-scoring relations align with broad relations such as `contains`, which makes the directional score large on one side while the reverse direction remains weak.

Therefore, the current metric should be interpreted as:

- a first-round reverse-overlap proxy

rather than as:

- a clean inverse-family measure

## Reassessment of the First-Round Result

The first-round inverse experiment should now be recorded as a mixed outcome rather than a success.

### What Did Work

The experiment was still useful in several important ways:

- the inverse-related score distribution was not degenerate
- the merge pipeline and mapping-interaction follow-up both ran successfully
- the bucket summaries revealed that the signal is not random noise
- the high-score bucket does show a potentially interesting “strong inverse-like support” subgroup

In particular, for `test_support >= 5`, the bucket:

- `(0.5, 1.0]`

shows:

- higher `hits_mean` than the middle buckets
- lower `alpha_mean`
- lower `delta_mean`

This means the experiment did expose a potentially meaningful high-confidence subgroup.

### What Did Not Work

At the same time, the experiment did not support the original hypothesis in its simple monotonic form.

The main reasons are:

- the overall Spearman correlations go in the opposite direction of the original expectation
- the `zero` bucket is also relatively strong, which weakens any claim that “more inverse support” alone explains lower multiplicity
- the current signal is non-monotonic rather than smoothly decreasing
- the metric definition is broad enough to capture reverse containment and other overlap patterns that are not clean inverse structure

Therefore, the correct status is:

- not “experiment successful”
- not “experiment useless”
- but “first-round proxy is too coarse, and the observed signal is mixed”

### Best Current Interpretation

The most defensible interpretation at this stage is:

> very strong inverse-like support may be associated with lower multiplicity, but naive directional reverse-overlap is too broad to isolate that effect cleanly.

Equivalently:

- `zero` inverse support does not imply difficulty
- weak or medium directional reverse overlap often behaves like an ambiguous structural regime
- only the highest-score subgroup currently looks consistent with the original intuition

This is better described as a threshold-like or non-monotonic pattern than as a linear inverse-strength effect.

## Recommended Next-Step Strategy

The current inverse line should proceed under a short decision workflow rather than open-ended exploration.

### Step 1: Upgrade the Metric Family

Do not rely only on the current directional score. The next iteration should add stricter relation-level variables, for example:

- `directional_inverse_strength`
- `mutual_inverse_strength`
- `inverse_clarity`

The intended roles are:

- `directional_inverse_strength`: preserve the current one-sided overlap baseline
- `mutual_inverse_strength`: require two-way agreement, so reverse containment is penalized
- `inverse_clarity`: distinguish a relation with one clear partner from a relation that overlaps weakly with many candidates

### Step 2: Re-run the Merge Analysis With the Stricter Metrics

The next analysis should focus less on a single global Spearman coefficient and more on:

- whether a high-confidence inverse subgroup becomes cleaner
- whether middle buckets remain the most unstable group
- whether the pattern still depends strongly on `mapping_type`

### Step 3: Make a Fast Keep-or-Drop Decision

After one stricter rerun:

- if a clearer high-confidence subgroup emerges, keep inverse as a secondary thesis result
- if the signal remains unstable, stop expanding this line and write it up as a failure-analysis result

This keeps the inverse section productive without letting it consume excessive thesis time.

## How This Should Be Written If the Rerun Still Fails

If the stricter metric family still does not produce a stable relation-level association, the inverse section should be written as a negative result.

The recommended thesis-style wording would be:

- the naive directional inverse proxy is too broad
- it captures reverse containment and other reverse-overlap structures
- therefore it does not provide a stable explanation for multiplicity
- stricter inverse-like definitions are needed for future work

This is a legitimate contribution to the thesis record because it documents why a seemingly reasonable structural proxy did not yield a clean explanatory result on `FB15k-237`.

## V2 Rerun With Stricter Metrics

The stricter rerun has now been implemented and executed.

### New Code Path

The first-round scripts were kept unchanged as the directional baseline.

The new v2 code path is:

- `Multiplicity_rewrite/inverse_relation_stats_v2.py`
- `Multiplicity_rewrite/inverse_analysis_v2.py`
- `Multiplicity_rewrite/inverse_mapping_interaction_analysis_v2.py`
- `Multiplicity_rewrite/inverse_v2_utils.py`

The purpose of this split is to preserve:

- the first-round directional experiment as a reproducible baseline
- the stricter rerun as a separate second-round attempt

### New Output Directory

The v2 outputs are stored under:

- `results/RotatE_FB15k237/inverse_v2/`

Current files include:

- `relation_inverse_stats_v2.csv`
- `relation_inverse_pair_scores_v2.csv`
- `relation_inverse_stats_summary_v2.txt`
- `relation_inverse_multiplicity_merged_v2.csv`
- `correlation_stats_v2.csv`
- `bucket_stats_v2.csv`
- `analysis_summary_v2.txt`
- `mapping_interaction/correlation_by_mapping_type_v2.csv`
- `mapping_interaction/bucket_stats_by_mapping_type_v2.csv`
- `mapping_interaction/summary_v2.txt`

### V2 Metric Design

The v2 rerun no longer relies on only one inverse variable.

It now keeps three relation-level variables:

- `directional_inverse_strength`
- `mutual_inverse_strength`
- `inverse_clarity`

Their intended roles are:

- `directional_inverse_strength`: preserve the original one-sided reverse-overlap baseline
- `mutual_inverse_strength`: penalize one-sided containment by requiring two-way support
- `inverse_clarity`: measure whether the best mutual partner is clearly better than the second-best one

### Main V2 Result

The stricter v2 metrics do not reverse the overall first-round conclusion.

At `test_support >= 10`:

- `mutual_inverse_strength` vs `hits_r`: `-0.2741`
- `mutual_inverse_strength` vs `alpha_r`: `0.2292`
- `mutual_inverse_strength` vs `delta_r`: `0.2212`

For `inverse_clarity` at the same threshold:

- `inverse_clarity` vs `hits_r`: `-0.2796`
- `inverse_clarity` vs `alpha_r`: `0.2398`
- `inverse_clarity` vs `delta_r`: `0.2263`

Therefore, even after the stricter rerun, the inverse-family section still does not support a simple global monotonic claim of the form:

> stronger inverse support leads to lower multiplicity.

### What Improved In V2

Although the global sign did not flip, the high-confidence subgroup became noticeably cleaner.

For `test_support >= 10`:

- `mutual_inverse_strength > 0.5`:
  - `n = 10`
  - `hits_mean = 0.6838`
  - `alpha_mean = 0.0971`
  - `delta_mean = 0.0627`

Compared with the middle mutual buckets, this subgroup is:

- more accurate
- less multiplicity-prone
- more structurally interpretable

For `inverse_clarity > 0.5`:

- `n = 5`
- `hits_mean = 0.8000`
- `alpha_mean = 0.0000`
- `delta_mean = 0.0000`

This is too small to support a broad claim, but it does indicate that:

- very high-confidence inverse-like relations can form a clean subgroup under the stricter metric family

### Interpretation After V2

The v2 rerun supports a narrower claim than the original hypothesis.

The safest current interpretation is:

- stricter inverse-like metrics improve subgroup purity
- very high-confidence mutual or clear inverse-like relations can look stable
- but the overall inverse signal is still dominated by mixed structural regimes
- therefore inverse remains a threshold-like or subgroup-based finding, not a global explanatory variable

### Mapping-Type View After V2

The mapping-type interaction still matters after the stricter rerun.

Current reading:

- `1-N` and `M-1` still do not show a clean beneficial inverse effect
- `M-N` contains some of the cleaner high-confidence subgroups under the stricter metrics
- `1-1` looks favorable, but the sample size is too small for a strong thesis claim
- the highest-confidence subgroup is concentrated mainly in `M-N`, with a small number of especially clean `1-1` cases

So the v2 rerun reduces some noise, but it does not remove the need to treat inverse as a structurally interacting variable rather than a standalone global factor.

## Current Decision After V2

After the stricter rerun, the inverse line should still be kept below `mapping type` in thesis priority.

The recommended status is now:

- keep `mapping type` as the main structural result
- keep inverse as an exploratory secondary subsection
- if needed, present the v2 high-confidence subgroup as a limited positive observation
- avoid presenting inverse as a universal main finding

If further time is invested, the most valuable next step is no longer another broad rerun, but:

- targeted case-study inspection of the high-confidence v2 subgroup
- followed by a final keep-or-drop decision for thesis writing

## V2 Case-Oriented Inspection

After the stricter rerun, the most useful follow-up is no longer another broad statistical pass, but targeted inspection of the high-confidence subgroup.

The purpose of this case-oriented inspection is to answer a narrower question:

> when stricter inverse-like metrics become very high, do the corresponding relations actually look more accurate and less multiplicity-prone?

This is a subgroup question, not a claim about the global trend.

### Case-Selection Principle

The current case inspection uses the following practical rule:

- first restrict to `test_support >= 10`
- then prioritize relations with high `mutual_inverse_strength` and/or high `inverse_clarity`
- then examine whether their `hits_r`, `alpha_r`, and `delta_r` match the intuitive “stable inverse-like” expectation

The cases are organized into three categories:

- positive cases
- negative cases
- boundary cases

The distinction is important:

- a positive case supports the inverse-like subgroup story
- a negative case shows why inverse cannot be written as a universal law
- a boundary case shows that low multiplicity and high accuracy need not move together perfectly

### Positive Cases

These are the strongest currently available examples in which stricter inverse-like support coincides with strong predictive stability.

#### Educational Institution / Campus

Pair:

- `/education/educational_institution_campus/educational_institution`
- `/education/educational_institution/campuses`

Key statistics:

- `mutual_inverse_strength = 0.8026`
- `inverse_clarity = 0.7770 / 0.7710`
- `overlap_jaccard = 0.6703`
- both relations have `hits_r = 1.0000`
- both relations have `alpha_r = 0.0000`
- both relations have `delta_r = 0.0000`

Interpretation:

- this is the cleanest available positive case
- the pair is strongly mutual, highly distinctive, and nearly ideal from the multiplicity perspective
- this pair is very suitable as a thesis case study for the “high-confidence inverse-like subgroup” claim

#### Olympics Sports / Athlete-Affiliation Structure

Pair:

- `/olympics/olympic_games/sports`
- `/olympics/olympic_sport/athletes./olympics/olympic_athlete_affiliation/olympics`

Key statistics:

- `mutual_inverse_strength = 0.5014`
- `inverse_clarity = 0.5014`
- `overlap_jaccard = 0.3346`
- `hits_r = 1.0000`
- `alpha_r = 0.0000`
- `delta_r = 0.0000`

Interpretation:

- this is an important positive case because it is not `1-1`
- it shows that a clean inverse-like subgroup can also appear inside `M-N`
- therefore the positive subgroup is not restricted only to trivially one-to-one structural pairs

#### User-Domain Olympics Sports

Relation:

- `/user/jg/default_domain/olympic_games/sports`

Best mutual partner:

- `/olympics/olympic_sport/athletes./olympics/olympic_athlete_affiliation/olympics`

Key statistics:

- `mutual_inverse_strength = 0.4532`
- `inverse_clarity = 0.4532`
- `hits_r = 0.9870`
- `alpha_r = 0.0455`
- `delta_r = 0.0455`

Interpretation:

- this is a useful supporting positive case
- the inverse-like score is not extreme in the way the education pair is, but the relation is still very stable
- it strengthens the claim that some high-confidence inverse-like relations do align with low multiplicity

#### Award Honored-For / Nominated-For

Relation:

- `/award/award_winning_work/awards_won./award/award_honor/honored_for`

Best mutual partner:

- `/award/award_nominated_work/award_nominations./award/award_nomination/nominated_for`

Key statistics:

- `mutual_inverse_strength = 0.3104`
- `inverse_clarity = 0.2799`
- `hits_r = 0.9000`
- `alpha_r = 0.0000`
- `delta_r = 0.0000`

Interpretation:

- this is not among the strongest structural pairs by score
- but it is still useful because it shows that a moderately strong inverse-like pair can look very stable
- this case is better treated as a secondary supporting example rather than a flagship one

### Negative Cases

These are the most important counterexamples because they show why the inverse section cannot be written as a universal monotonic result.

#### Award Winner / Award Nominee

Pair:

- `/award/award_winner/awards_won./award/award_honor/award_winner`
- `/award/award_nominee/award_nominations./award/award_nomination/award_nominee`

Key statistics:

- `mutual_inverse_strength = 0.5138`
- `inverse_clarity = 0.4917 / 0.4952`
- `overlap_jaccard = 0.3458`

Multiplicity side:

- winner side: `hits_r = 0.6150`, `alpha_r = 0.1964`, `delta_r = 0.0893`
- nominee side: `hits_r = 0.7784`, `alpha_r = 0.1271`, `delta_r = 0.0650`

Interpretation:

- this pair is genuinely strong by the stricter inverse-like metrics
- however, it is not uniformly low-multiplicity
- this makes it a good negative case against the naive statement that “high inverse-like support automatically implies low multiplicity”

#### Award Winner / Nominated-For

Pair:

- `/award/award_winning_work/awards_won./award/award_honor/award_winner`
- `/award/award_nominee/award_nominations./award/award_nomination/nominated_for`

Key statistics:

- `mutual_inverse_strength = 0.5006`
- `inverse_clarity = 0.3463 / 0.3691`
- `overlap_jaccard = 0.3339`

Multiplicity side:

- winner side: `hits_r = 0.3929`, `alpha_r = 0.2273`, `delta_r = 0.1818`
- nominated-for side: `hits_r = 0.3534`, `alpha_r = 0.3879`, `delta_r = 0.2586`

Interpretation:

- this is the clearest negative case in the current v2 subgroup
- despite a fairly strong mutual score, both relations remain difficult and multiplicity-prone
- it strongly supports the conclusion that reverse structural alignment alone is not sufficient to explain stability

#### Language Countries-Spoken-In / Official-Language

Pair:

- `/language/human_language/countries_spoken_in`
- `/location/country/official_language`

Key statistics:

- `mutual_inverse_strength = 0.4679`
- `inverse_clarity = 0.4679`
- `overlap_jaccard = 0.3054`

Multiplicity side:

- language side: `hits_r = 0.5371`, `alpha_r = 0.4706`, `delta_r = 0.2647`
- country side: `hits_r = 0.4866`, `alpha_r = 0.1765`, `delta_r = 0.1176`

Interpretation:

- this is a useful semantic counterexample
- the pair looks intuitively related and has a respectable mutual score
- yet the multiplicity pattern is not clean at all, especially on the language side
- this reinforces the view that inverse-like structure interacts with relation difficulty and semantic heterogeneity

#### Film Distributor / Production Companies

Pair:

- `/film/film_distributor/films_distributed./film/film_film_distributor_relationship/film`
- `/film/film/production_companies`

Key statistics:

- `mutual_inverse_strength = 0.3688`
- `inverse_clarity = 0.3455 / 0.3272`
- `overlap_jaccard = 0.2261`

Multiplicity side:

- distributor side: `hits_r = 0.4353`, `alpha_r = 0.2671`, `delta_r = 0.1180`
- production-company side: `hits_r = 0.5502`, `alpha_r = 0.2286`, `delta_r = 0.0952`

Interpretation:

- the structural score is not negligible
- but the pair does not yield low multiplicity
- this is another useful counterexample showing that moderate inverse-like support can still coexist with unstable behavior

### Boundary Cases

These cases are neither fully positive nor fully negative. They are useful because they reveal that `accuracy` and `multiplicity` do not always move together perfectly.

#### Soccer Roster Position / Team

Relations:

- `/soccer/football_team/current_roster./soccer/football_roster_position/position`
- `/soccer/football_team/current_roster./sports/sports_team_roster/position`

Shared best mutual partner:

- `/sports/sports_position/players./sports/sports_team_roster/team`

Key statistics:

- `mutual_inverse_strength = 0.6397` and `0.6345`
- `inverse_clarity = 0.6397` and `0.6345`
- `overlap_jaccard ≈ 0.4703` and `0.4647`

Multiplicity side:

- both soccer relations have `hits_r = 0.5000`
- both soccer relations have `alpha_r = 0.0000`
- both soccer relations have `delta_r = 0.0000`

Interpretation:

- these are not negative cases, because multiplicity is extremely low
- but they are not ideal positive cases either, because the accuracy is only moderate
- therefore they show an important boundary phenomenon:
  high-confidence inverse-like support may reduce disagreement without guaranteeing very high predictive accuracy

This distinction is valuable for thesis writing, because it avoids conflating:

- stability

with:

- overall difficulty

### Current Case-Level Conclusion

The case inspection supports a more precise and more defensible interpretation than either a pure success story or a pure failure story.

The current safest conclusion is:

- some very high-confidence inverse-like relations are indeed highly accurate and almost multiplicity-free
- however, this pattern is not universal even within the high-score subgroup
- therefore inverse should be described as revealing a small, interpretable, high-confidence subgroup rather than a global monotonic law

More concretely:

- the strongest positive cases are best treated as qualitative support for the subgroup story
- the strongest negative cases should be retained to prevent overclaiming
- the soccer-style boundary cases are useful to explain why low multiplicity and high accuracy should not be collapsed into the same concept

### Recommended Thesis Use

If this section is retained in the thesis, the current best use is:

1. present the first-round directional metric as too broad
2. present the v2 metric family as a stricter rerun
3. report that the global trend still does not become clean
4. then use the case inspection to argue that a limited high-confidence inverse-like subgroup does exist

This is currently the most rigorous way to preserve the useful part of the inverse line without overstating its scope.

## TransE Follow-Up Has Now Been Completed

The planned `TransE` comparison has now been run.

This means the inverse section is no longer only a `RotatE`-internal exploration. It now has a first cross-model comparison under the same dataset and repeated-run multiplicity setup.

## TransE Setup

The `TransE` follow-up uses:

- model: `TransE`
- dataset: `FB15k-237`
- experiment folder: `LibKGE/local/multiplicity/TransE_FB15k237_N`
- repeated runs: `seed_0` to `seed_7`

The `_N` run family is used to stay aligned with the current `Hits@10`-based evaluation convention.

The workflow reused existing repeated runs rather than retraining.

## TransE Code Path

The `TransE` inverse comparison keeps the same `v1` / `v2` split already used for `RotatE`.

Current scripts:

- `Multiplicity_rewrite/inverse_relation_stats.py`
- `Multiplicity_rewrite/inverse_analysis.py`
- `Multiplicity_rewrite/inverse_mapping_interaction_analysis.py`
- `Multiplicity_rewrite/inverse_relation_stats_v2.py`
- `Multiplicity_rewrite/inverse_analysis_v2.py`
- `Multiplicity_rewrite/inverse_mapping_interaction_analysis_v2.py`

The analysis was run in the local `LibKGE` conda environment.

## TransE Output Directories

The `TransE` outputs are now stored under:

- `results/TransE_FB15k237_N/inverse/`
- `results/TransE_FB15k237_N/inverse_v2/`

with the corresponding mapping-type interaction outputs under:

- `results/TransE_FB15k237_N/inverse/mapping_interaction/`
- `results/TransE_FB15k237_N/inverse_v2/mapping_interaction/`

## TransE V1 Result

The first-round directional inverse result under `TransE` is extremely similar in shape to the original `RotatE` result.

For `test_support >= 10`:

- `Spearman(inverse_strength, hits_r) = -0.2870`
- `Spearman(inverse_strength, alpha_r) = 0.2221`
- `Spearman(inverse_strength, delta_r) = 0.2595`

The bucket structure is also the same familiar pattern:

- `zero`: strong average performance and relatively low multiplicity
- low-to-mid nonzero buckets: clearly worse
- `(0.5, 1.0]`: partial recovery in `hits` and lower `alpha/delta`, but not enough to overturn the global trend

For `test_support >= 10`, the v1 bucket means are:

- `zero`:
  - `hits_mean = 0.6480`
  - `alpha_mean = 0.2565`
  - `delta_mean = 0.1452`
- `(0.5, 1.0]`:
  - `hits_mean = 0.6162`
  - `alpha_mean = 0.2011`
  - `delta_mean = 0.1145`

This is important because it means:

- `TransE` does not rescue the naive directional inverse hypothesis either
- the apparent threshold-like shape was not unique to `RotatE`

## TransE V2 Result

The stricter `v2` rerun again improves subgroup quality without changing the global conclusion.

For `test_support >= 10`:

- `mutual_inverse_strength`:
  - `Spearman(hits_r) = -0.2761`
  - `Spearman(alpha_r) = 0.2137`
  - `Spearman(delta_r) = 0.2290`
- `inverse_clarity`:
  - `Spearman(hits_r) = -0.2819`
  - `Spearman(alpha_r) = 0.2371`
  - `Spearman(delta_r) = 0.2427`

So the stricter metrics still do **not** produce a clean global inverse story in `TransE`.

But the subgroup view remains meaningful.

For `test_support >= 10`:

- `mutual_inverse_strength > 0.5`:
  - `n = 10`
  - `hits_mean = 0.6866`
  - `alpha_mean = 0.1361`
  - `delta_mean = 0.0813`
- `inverse_clarity > 0.5`:
  - `n = 5`
  - `hits_mean = 0.8000`
  - `alpha_mean = 0.0000`
  - `delta_mean = 0.0000`

This is very close in shape to the earlier `RotatE` reading.

## Direct Comparison With RotatE

The most important cross-model observation is not a difference, but a structural similarity.

Under both `RotatE` and `TransE`:

- the global correlation between inverse-like strength and multiplicity is still unfavorable
- the zero-inverse group remains strong
- the middle buckets remain noisy and often worse
- the very-high-confidence subgroup still looks cleaner

This means the inverse line should still be read as:

- not a universal global law
- but not a total failure either
- rather, a threshold-like or subgroup-based phenomenon

## Mapping-Type Interaction Under TransE

The mapping-type interaction also remains important under `TransE`.

For `test_support >= 10`:

- `1-N` and `M-1` still show clearly unfavorable correlations
- `M-N` still contains part of the cleaner high-confidence subgroup
- `1-1` still looks favorable, but the sample size is small

Examples from the `TransE` v2 interaction summary:

- `1-N`, `mutual_inverse_strength`:
  - `Spearman(hits_r) = -0.4302`
  - `Spearman(alpha_r) = 0.4652`
  - `Spearman(delta_r) = 0.6160`
- `M-1`, `mutual_inverse_strength`:
  - `Spearman(hits_r) = -0.4299`
  - `Spearman(alpha_r) = 0.4681`
  - `Spearman(delta_r) = 0.5550`
- `M-N`, `mutual_inverse_strength`:
  - `Spearman(hits_r) = -0.3251`
  - `Spearman(alpha_r) = 0.0730`
  - `Spearman(delta_r) = 0.0408`

So the same methodological warning still applies:

- inverse is interacting with mapping structure
- it should not be presented as an independent global factor

## Updated Interpretation After The TransE Comparison

After adding the `TransE` comparison, the inverse line becomes easier to position.

The cross-model result suggests:

- the naive directional inverse proxy is broadly unstable across models
- the stricter `v2` family improves subgroup purity in both models
- but neither model supports a clean monotonic global inverse explanation
- therefore the most defensible use of inverse is still as a limited subgroup observation

This strengthens the writing strategy already adopted for the `RotatE` version.

## Updated Current Status

The recommended thesis positioning is now:

- `mapping type` remains the main structural result
- `inverse` remains an exploratory secondary result
- the strongest use of `inverse` is the cross-model-consistent high-confidence subgroup story
- `inverse` should still not be written as a universal explanatory pattern

In other words:

- `TransE` does not overturn the inverse conclusion
- it mostly confirms the same constrained interpretation already reached with `RotatE`
