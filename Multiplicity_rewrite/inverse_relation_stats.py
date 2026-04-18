import argparse
import os

import pandas as pd

from kge import Config
from kge import Dataset
from kge.util.seed import seed_from_config


DEFAULT_EXPERIMENTS_ROOT = "LibKGE/local/multiplicity"
DEFAULT_EXPERIMENT_NAME = "RotatE_FB15k237"
DEFAULT_OUTPUT_DIR = "results/RotatE_FB15k237/inverse"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute relation-level inverse statistics from the training graph."
    )
    parser.add_argument(
        "--experiments-root",
        default=DEFAULT_EXPERIMENTS_ROOT,
        help="Root directory containing multiplicity experiment folders",
    )
    parser.add_argument(
        "--experiment-name",
        default=DEFAULT_EXPERIMENT_NAME,
        help="Experiment folder name, e.g. RotatE_FB15k237",
    )
    parser.add_argument(
        "--reference-run",
        default="seed_0",
        help="Run folder used only to locate config.yaml and dataset metadata",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for inverse statistics outputs",
    )
    return parser.parse_args()


def load_dataset_from_run(run_dir):
    config_path = os.path.join(run_dir, "config.yaml")
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"config.yaml not found: {config_path}")

    config = Config()
    config.load(config_path)
    config.folder = run_dir
    Dataset._abort_when_cache_outdated = False
    seed_from_config(config)
    return Dataset.create(config)


def build_relation_edge_sets(train_triples, num_relations):
    edge_sets = [set() for _ in range(num_relations)]
    reverse_edge_sets = [set() for _ in range(num_relations)]

    for triple in train_triples.tolist():
        head, relation, tail = triple
        edge_sets[relation].add((head, tail))
        reverse_edge_sets[relation].add((tail, head))

    return edge_sets, reverse_edge_sets


def compute_inverse_tables(dataset):
    relation_names = list(dataset.relation_ids())
    num_relations = dataset.num_relations()
    train_triples = dataset.split("train")
    edge_sets, reverse_edge_sets = build_relation_edge_sets(train_triples, num_relations)
    train_supports = [len(edges) for edges in edge_sets]

    pair_rows = []
    relation_rows = []

    for source_relation_id in range(num_relations):
        source_edges = edge_sets[source_relation_id]
        source_support = train_supports[source_relation_id]

        best_partner_id = None
        best_score = -1.0
        best_overlap = 0

        for target_relation_id in range(num_relations):
            if source_relation_id == target_relation_id:
                continue

            target_reverse_edges = reverse_edge_sets[target_relation_id]
            overlap_count = len(source_edges & target_reverse_edges)

            if source_support == 0:
                inverse_score = 0.0
            else:
                inverse_score = overlap_count / source_support

            pair_rows.append(
                {
                    "source_relation_id": source_relation_id,
                    "source_relation_name": relation_names[source_relation_id],
                    "target_relation_id": target_relation_id,
                    "target_relation_name": relation_names[target_relation_id],
                    "source_train_support": source_support,
                    "target_train_support": train_supports[target_relation_id],
                    "overlap_count": overlap_count,
                    "inverse_score": inverse_score,
                }
            )

            if (
                inverse_score > best_score
                or (
                    inverse_score == best_score
                    and best_partner_id is not None
                    and target_relation_id < best_partner_id
                )
                or best_partner_id is None
            ):
                best_partner_id = target_relation_id
                best_score = inverse_score
                best_overlap = overlap_count

        relation_rows.append(
            {
                "relation_id": source_relation_id,
                "relation_name": relation_names[source_relation_id],
                "train_support": source_support,
                "inverse_strength": best_score,
                "best_inverse_partner_id": best_partner_id,
                "best_inverse_partner_name": (
                    relation_names[best_partner_id] if best_partner_id is not None else ""
                ),
                "best_inverse_score": best_score,
                "best_inverse_overlap_count": best_overlap,
            }
        )

    return relation_rows, pair_rows


def main():
    args = parse_args()
    run_dir = os.path.join(
        args.experiments_root,
        args.experiment_name,
        args.reference_run,
    )
    if not os.path.isdir(run_dir):
        raise FileNotFoundError(f"Reference run directory does not exist: {run_dir}")

    dataset = load_dataset_from_run(run_dir)
    relation_rows, pair_rows = compute_inverse_tables(dataset)

    os.makedirs(args.output_dir, exist_ok=True)
    relation_output = os.path.join(args.output_dir, "relation_inverse_stats.csv")
    pair_output = os.path.join(args.output_dir, "relation_inverse_pair_scores.csv")

    pd.DataFrame(relation_rows).to_csv(relation_output, index=False)
    pd.DataFrame(pair_rows).to_csv(pair_output, index=False)

    print(f"Saved relation-level inverse stats to: {relation_output}")
    print(f"Saved pair-level inverse scores to: {pair_output}")


if __name__ == "__main__":
    main()
