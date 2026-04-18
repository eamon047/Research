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


def create_combined_rows(
    head_rank_outputs,
    tail_rank_outputs,
    query_relations,
    jobs,
    config,
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
    stacked_head_ranks = [rank.cpu() for rank in head_rank_outputs]
    stacked_tail_ranks = [rank.cpu() for rank in tail_rank_outputs]

    rows = []
    for relation_id in range(dataset.num_relations()):
        test_support = int(test_support_per_relation[relation_id].item())
        head_support = test_support
        tail_support = test_support

        relation_mask = query_relations == relation_id
        relation_query_count = int(torch.sum(relation_mask).item())

        if relation_query_count == 0:
            hits_r = float("nan")
            alpha_r = float("nan")
            delta_r = float("nan")
            eligible_support = 0
        else:
            relation_rank_outputs = []
            for head_rank, tail_rank in zip(stacked_head_ranks, stacked_tail_ranks):
                combined_rank = torch.cat(
                    [head_rank[relation_mask], tail_rank[relation_mask]], dim=0
                )
                relation_rank_outputs.append(combined_rank)

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
                "test_support": test_support,
                "head_support": head_support,
                "tail_support": tail_support,
                "eligible_support": eligible_support,
                "hits_r": hits_r,
                "alpha_r": alpha_r,
                "delta_r": delta_r,
            }
        )

    return rows


def run_relation_multiplicity_combined_export(config):
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

    rows = create_combined_rows(
        head_rank_outputs,
        tail_rank_outputs,
        query_relations,
        jobs,
        config,
    )
    df = pd.DataFrame(rows)

    output_dir = os.path.dirname(config.output_csv)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    df.to_csv(config.output_csv, index=False)
    print(f"Saved combined relation-level results to: {config.output_csv}")


def main():
    defaults = default_local_experiment_config(
        output_csv=(
            "results/RotatE_FB15k237/mapping_type/combined/"
            "relation_metrics_num7_agg7_k10.csv"
        )
    )
    args = parse_local_experiment_args(
        description="Export combined relation-level multiplicity analysis.",
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
    run_relation_multiplicity_combined_export(config)


if __name__ == "__main__":
    main()
