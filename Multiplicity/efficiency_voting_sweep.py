import argparse
import itertools
import math
import os
import random

import pandas as pd

from multiplicity_utils import (
    borda_scoring,
    compute_rank_outputs,
    evaluate_rank_outputs,
    load_jobs_from_experiment,
    majority_scoring,
    range_scoring,
    resolve_run_directories,
)


SCORING_FUNCTIONS = {
    "without": None,
    "major": majority_scoring,
    "borda": borda_scoring,
    "range": range_scoring,
}


def parse_int_list(value):
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def select_pool_indices(num_jobs, pool_size, seed, mode):
    if pool_size > num_jobs:
        raise ValueError(f"pool_size={pool_size} exceeds available jobs={num_jobs}")

    if mode == "first":
        return list(range(pool_size))
    if mode == "sample":
        rng = random.Random(seed)
        return sorted(rng.sample(list(range(num_jobs)), pool_size))

    raise ValueError(f"Unknown pool selection mode: {mode}")


def sample_shared_pool_communities(pool_indices, num_communities, community_size, seed):
    if num_communities > len(pool_indices):
        raise ValueError(
            f"num_communities={num_communities} exceeds pool size={len(pool_indices)}"
        )
    if community_size > len(pool_indices):
        raise ValueError(
            f"community_size={community_size} exceeds pool size={len(pool_indices)}"
        )
    if community_size < 1:
        raise ValueError("community_size must be at least 1")

    rng = random.Random(seed)
    baseline_indices = rng.sample(pool_indices, num_communities)
    communities = []
    for baseline_index in baseline_indices:
        other_candidates = [
            index for index in pool_indices if index != baseline_index
        ]
        other_indices = rng.sample(other_candidates, community_size - 1)
        communities.append(other_indices + [baseline_index])
    return communities


def community_overlap_stats(communities):
    community_sets = [set(community) for community in communities]
    unique_model_count = len(set().union(*community_sets))
    pairwise_overlaps = []
    pairwise_jaccards = []

    for left, right in itertools.combinations(community_sets, 2):
        intersection = len(left & right)
        union = len(left | right)
        pairwise_overlaps.append(intersection)
        pairwise_jaccards.append(intersection / union if union else math.nan)

    if not pairwise_overlaps:
        avg_overlap = math.nan
        avg_jaccard = math.nan
    else:
        avg_overlap = sum(pairwise_overlaps) / len(pairwise_overlaps)
        avg_jaccard = sum(pairwise_jaccards) / len(pairwise_jaccards)

    return {
        "unique_model_count": unique_model_count,
        "avg_pairwise_overlap": avg_overlap,
        "avg_pairwise_jaccard": avg_jaccard,
    }


def format_members(indices, run_names):
    return ";".join(run_names[index] for index in indices)


def format_communities(communities, run_names):
    return "|".join(format_members(community, run_names) for community in communities)


def safe_ratio(numerator, denominator):
    if denominator is None or math.isnan(denominator) or denominator == 0:
        return math.nan
    if numerator is None or math.isnan(numerator):
        return math.nan
    return numerator / denominator


def add_derived_metrics(df, reference_community_size):
    df = df.copy()
    df["alpha_reduction"] = math.nan
    df["delta_reduction"] = math.nan
    df["alpha_recovery_vs_reference"] = math.nan
    df["delta_recovery_vs_reference"] = math.nan

    key_cols = ["pool_size", "num_communities", "sampling_seed", "baseline"]
    lookup = {
        tuple(row[col] for col in key_cols + ["community_size"]): row
        for _, row in df.iterrows()
    }

    for index, row in df.iterrows():
        base_key = (
            row["pool_size"],
            row["num_communities"],
            row["sampling_seed"],
            "without",
            row["community_size"],
        )
        without_row = lookup.get(base_key)
        if without_row is None:
            continue

        alpha_reduction = safe_ratio(
            without_row["Alpha"] - row["Alpha"], without_row["Alpha"]
        )
        delta_reduction = safe_ratio(
            without_row["Delta"] - row["Delta"], without_row["Delta"]
        )

        if row["baseline"] == "without":
            alpha_reduction = 0.0
            delta_reduction = 0.0

        df.at[index, "alpha_reduction"] = alpha_reduction
        df.at[index, "delta_reduction"] = delta_reduction

        if row["baseline"] == "without":
            continue

        reference_without = lookup.get(
            (
                row["pool_size"],
                row["num_communities"],
                row["sampling_seed"],
                "without",
                reference_community_size,
            )
        )
        reference_voting = lookup.get(
            (
                row["pool_size"],
                row["num_communities"],
                row["sampling_seed"],
                row["baseline"],
                reference_community_size,
            )
        )
        if reference_without is None or reference_voting is None:
            continue

        alpha_reference_gain = reference_without["Alpha"] - reference_voting["Alpha"]
        delta_reference_gain = reference_without["Delta"] - reference_voting["Delta"]
        alpha_current_gain = without_row["Alpha"] - row["Alpha"]
        delta_current_gain = without_row["Delta"] - row["Delta"]

        df.at[index, "alpha_recovery_vs_reference"] = safe_ratio(
            alpha_current_gain, alpha_reference_gain
        )
        df.at[index, "delta_recovery_vs_reference"] = safe_ratio(
            delta_current_gain, delta_reference_gain
        )

    return df


def run_sweep(args):
    pool_sizes = parse_int_list(args.pool_sizes)
    community_sizes = parse_int_list(args.community_sizes)
    sampling_seeds = parse_int_list(args.sampling_seeds)
    baselines = [item.strip() for item in args.baselines.split(",") if item.strip()]

    unknown_baselines = [
        baseline for baseline in baselines if baseline not in SCORING_FUNCTIONS
    ]
    if unknown_baselines:
        raise ValueError(f"Unknown baselines: {unknown_baselines}")

    max_pool_size = max(pool_sizes)
    max_community_size = max(community_sizes)
    if args.reference_community_size not in community_sizes:
        raise ValueError(
            "--reference-community-size must be included in --community-sizes"
        )

    experiment_dir = os.path.join(args.experiments_root, args.experiment_name)
    run_dirs = resolve_run_directories(experiment_dir)
    run_names = [os.path.basename(path) for path in run_dirs]

    print(f"{args.model}-{args.dataset}")
    print(f"Loading runs from: {experiment_dir}")
    print(f"Available runs: {len(run_dirs)}")

    if max_pool_size > len(run_dirs):
        raise ValueError(
            f"max pool size={max_pool_size} exceeds available runs={len(run_dirs)}"
        )

    if args.plan_only:
        rows = []
        for pool_size in pool_sizes:
            for sampling_seed in sampling_seeds:
                pool_indices = select_pool_indices(
                    num_jobs=len(run_dirs),
                    pool_size=pool_size,
                    seed=sampling_seed,
                    mode=args.pool_mode,
                )
                for community_size in community_sizes:
                    communities = sample_shared_pool_communities(
                        pool_indices=pool_indices,
                        num_communities=args.num_communities,
                        community_size=community_size,
                        seed=sampling_seed,
                    )
                    rows.append(
                        {
                            "model": args.model,
                            "dataset": args.dataset,
                            "experiment_name": args.experiment_name,
                            "pool_mode": args.pool_mode,
                            "pool_size": pool_size,
                            "num_communities": args.num_communities,
                            "community_size": community_size,
                            "sampling_seed": sampling_seed,
                            "k": args.k,
                            "total_voting_slots": (
                                args.num_communities * community_size
                            ),
                            "pool_members": format_members(pool_indices, run_names),
                            "communities": format_communities(
                                communities, run_names
                            ),
                            **community_overlap_stats(communities),
                        }
                    )

        df = pd.DataFrame(rows)
        output_dir = os.path.dirname(args.output_csv)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        df.to_csv(args.output_csv, index=False)
        print(f"Saved planned sweep settings to: {args.output_csv}")
        return

    jobs = load_jobs_from_experiment(
        experiment_dir,
        num_required=max_pool_size,
        agg_num_required=max_community_size,
    )

    rows = []
    for pool_size in pool_sizes:
        for sampling_seed in sampling_seeds:
            pool_indices = select_pool_indices(
                num_jobs=len(jobs),
                pool_size=pool_size,
                seed=sampling_seed,
                mode=args.pool_mode,
            )

            for community_size in community_sizes:
                communities = sample_shared_pool_communities(
                    pool_indices=pool_indices,
                    num_communities=args.num_communities,
                    community_size=community_size,
                    seed=sampling_seed,
                )
                overlap_stats = community_overlap_stats(communities)
                common_fields = {
                    "model": args.model,
                    "dataset": args.dataset,
                    "experiment_name": args.experiment_name,
                    "pool_mode": args.pool_mode,
                    "pool_size": pool_size,
                    "num_communities": args.num_communities,
                    "community_size": community_size,
                    "sampling_seed": sampling_seed,
                    "k": args.k,
                    "total_voting_slots": args.num_communities * community_size,
                    "pool_members": format_members(pool_indices, run_names),
                    "communities": format_communities(communities, run_names),
                    **overlap_stats,
                }

                print(
                    "Evaluating "
                    f"P={pool_size}, C={args.num_communities}, "
                    f"m={community_size}, seed={sampling_seed}"
                )
                for baseline in baselines:
                    rank_outputs, _query_relations = compute_rank_outputs(
                        jobs,
                        communities,
                        agg_func=SCORING_FUNCTIONS[baseline],
                        include_relations=False,
                    )
                    metrics = evaluate_rank_outputs(rank_outputs, args.k)
                    rows.append(
                        {
                            **common_fields,
                            "baseline": baseline,
                            "Hits": metrics["mean_hits"],
                            "Epsilon": metrics["epsilon"],
                            "Alpha": metrics["ambiguity"],
                            "Delta": metrics["discrepancy"],
                            "eligible_support": metrics["eligible_support"],
                        }
                    )

    df = pd.DataFrame(rows)
    df = add_derived_metrics(df, args.reference_community_size)

    output_dir = os.path.dirname(args.output_csv)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    df.to_csv(args.output_csv, index=False)
    print(f"Saved sweep results to: {args.output_csv}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Run a shared model-pool voting sweep for the optional efficiency "
            "branch."
        )
    )
    parser.add_argument("--experiments-root", default="LibKGE/local")
    parser.add_argument("--model", default="RotatE")
    parser.add_argument("--dataset", default="FB15k237")
    parser.add_argument("--experiment-name", default="RotatE_FB15k237")
    parser.add_argument("--pool-sizes", default="10,20,30")
    parser.add_argument("--community-sizes", default="2,3,4,5,6,8")
    parser.add_argument("--num-communities", type=int, default=10)
    parser.add_argument("--sampling-seeds", default="0,1,2,3,4")
    parser.add_argument("--reference-community-size", type=int, default=8)
    parser.add_argument("--pool-mode", choices=["first", "sample"], default="first")
    parser.add_argument("--baselines", default="without,major,borda,range")
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Write planned settings and overlap stats without loading models.",
    )
    parser.add_argument(
        "--output-csv",
        default="results/RotatE_FB15k237/efficiency_voting/sweep_metrics.csv",
    )
    args = parser.parse_args()
    run_sweep(args)


if __name__ == "__main__":
    main()
