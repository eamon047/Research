import os

import pandas as pd
import torch

from multiplicity_utils import (
    LocalExperimentConfig,
    compute_rank_data,
    default_local_experiment_config,
    evaluate_rank_outputs,
    load_jobs_from_experiment,
    parse_local_experiment_args,
    sample_aggregation_indices,
)


def create_side_rows(
    rank_outputs,
    query_relations,
    jobs,
    config,
    side,
    baseline_name="without",
):
    dataset = jobs[0].dataset
    relation_names = dataset.relation_ids()
    relation_types = dataset.index("relation_types")
    test_support_per_relation = torch.bincount(
        query_relations.cpu(),
        minlength=dataset.num_relations(),
    )

    query_relations = query_relations.cpu()
    stacked_ranks = [rank.cpu() for rank in rank_outputs]

    rows = []
    for relation_id in range(dataset.num_relations()):
        test_support = int(test_support_per_relation[relation_id].item())
        side_support = test_support
        relation_mask = query_relations == relation_id
        relation_query_count = int(torch.sum(relation_mask).item())

        if relation_query_count == 0:
            hits_r = float("nan")
            alpha_r = float("nan")
            delta_r = float("nan")
            eligible_support = 0
        else:
            relation_rank_outputs = [rank[relation_mask] for rank in stacked_ranks]
            relation_metrics = evaluate_rank_outputs(relation_rank_outputs, config.k)
            hits_r = relation_metrics["mean_hits"]
            alpha_r = relation_metrics["ambiguity"]
            delta_r = relation_metrics["discrepancy"]
            eligible_support = relation_metrics["eligible_support"]

        rows.append(
            {
                "model": config.model,
                "dataset": config.dataset,
                "baseline": baseline_name,
                "relation_id": relation_id,
                "relation_name": relation_names[relation_id],
                "mapping_type": relation_types[relation_id],
                "side": side,
                "test_support": test_support,
                "side_support": side_support,
                "eligible_support": eligible_support,
                "hits_r": hits_r,
                "alpha_r": alpha_r,
                "delta_r": delta_r,
            }
        )

    return rows


def run_relation_mapping_analysis(config):
    experiment_dir = os.path.join(config.experiments_root, config.experiment_name)
    print(f"{config.model}-{config.dataset}")
    print(f"Loading runs from: {experiment_dir}")

    jobs = load_jobs_from_experiment(
        experiment_dir,
        num_required=config.num,
        agg_num_required=config.agg_num,
    )
    agg_index_list = sample_aggregation_indices(
        num_jobs=len(jobs),
        num=config.num,
        agg_num=config.agg_num,
        random_seed=config.random_seed,
    )

    head_rank_outputs = []
    tail_rank_outputs = []
    query_relations = None
    for agg_indices in agg_index_list:
        agg_jobs = [jobs[i] for i in agg_indices]
        rank_data = compute_rank_data(agg_jobs, agg_func=None, include_relations=True)
        head_rank_outputs.append(rank_data["s_ranks"])
        tail_rank_outputs.append(rank_data["o_ranks"])
        if query_relations is None:
            query_relations = rank_data["relations"]

    rows = []
    rows.extend(
        create_side_rows(
            head_rank_outputs,
            query_relations,
            jobs,
            config,
            side="head",
        )
    )
    rows.extend(
        create_side_rows(
            tail_rank_outputs,
            query_relations,
            jobs,
            config,
            side="tail",
        )
    )
    df = pd.DataFrame(rows)

    output_dir = os.path.dirname(config.output_csv)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    df.to_csv(config.output_csv, index=False)
    print(f"Saved relation-level results to: {config.output_csv}")


def main():
    defaults = default_local_experiment_config(
        output_csv=(
            "results/RotatE_FB15k237/mapping_type/by_side/"
            "relation_metrics_num7_agg7_k10.csv"
        )
    )
    args = parse_local_experiment_args(
        description="Export relation-level mapping-type multiplicity analysis.",
        default_output_csv=defaults.output_csv,
    )
    config = LocalExperimentConfig(
        experiments_root=args.experiments_root,
        model=args.model,
        dataset=args.dataset,
        experiment_name=args.experiment_name,
        num=args.num,
        agg_num=args.agg_num,
        k=args.k,
        random_seed=args.seed,
        output_csv=args.output_csv,
    )
    run_relation_mapping_analysis(config)


if __name__ == "__main__":
    main()
