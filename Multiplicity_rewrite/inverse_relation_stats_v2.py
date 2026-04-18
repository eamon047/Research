import argparse
import math
import os

from kge import Config
from kge import Dataset
from kge.util.seed import seed_from_config

from inverse_v2_utils import write_csv


DEFAULT_EXPERIMENTS_ROOT = "LibKGE/local/multiplicity"
DEFAULT_EXPERIMENT_NAME = "RotatE_FB15k237"
DEFAULT_OUTPUT_DIR = "results/RotatE_FB15k237/inverse_v2"


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Compute v2 inverse statistics from the training graph with both "
            "directional and stricter mutual metrics."
        )
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
        help="Directory for v2 inverse statistics outputs",
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


def harmonic_mean(x, y):
    if x == 0.0 or y == 0.0:
        return 0.0
    return 2.0 * x * y / (x + y)


def jaccard_score(overlap_count, left_support, right_support):
    union_size = left_support + right_support - overlap_count
    if union_size <= 0:
        return 0.0
    return overlap_count / union_size


def metric_record(
    score=-1.0,
    partner_id=None,
    partner_name="",
    overlap_count=0,
    forward_score=0.0,
    backward_score=0.0,
    jaccard=0.0,
):
    return {
        "score": score,
        "partner_id": partner_id,
        "partner_name": partner_name,
        "overlap_count": overlap_count,
        "forward_score": forward_score,
        "backward_score": backward_score,
        "jaccard": jaccard,
    }


def is_better_candidate(candidate, incumbent):
    if candidate["score"] > incumbent["score"]:
        return True
    if candidate["score"] < incumbent["score"]:
        return False
    if candidate["overlap_count"] > incumbent["overlap_count"]:
        return True
    if candidate["overlap_count"] < incumbent["overlap_count"]:
        return False
    if candidate["partner_id"] is None:
        return False
    if incumbent["partner_id"] is None:
        return True
    return candidate["partner_id"] < incumbent["partner_id"]


def finalize_record(record):
    if record["score"] <= 0.0:
        return metric_record(score=0.0)
    return record


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

        best_directional = metric_record()
        best_mutual = metric_record()
        second_best_mutual = metric_record()

        for target_relation_id in range(num_relations):
            if source_relation_id == target_relation_id:
                continue

            target_support = train_supports[target_relation_id]
            target_reverse_edges = reverse_edge_sets[target_relation_id]
            overlap_count = len(source_edges & target_reverse_edges)

            forward_score = overlap_count / source_support if source_support else 0.0
            backward_score = overlap_count / target_support if target_support else 0.0
            mutual_score = harmonic_mean(forward_score, backward_score)
            overlap_jaccard = jaccard_score(overlap_count, source_support, target_support)

            pair_rows.append(
                {
                    "source_relation_id": source_relation_id,
                    "source_relation_name": relation_names[source_relation_id],
                    "target_relation_id": target_relation_id,
                    "target_relation_name": relation_names[target_relation_id],
                    "source_train_support": source_support,
                    "target_train_support": target_support,
                    "overlap_count": overlap_count,
                    "directional_inverse_score": forward_score,
                    "reverse_directional_inverse_score": backward_score,
                    "mutual_inverse_score": mutual_score,
                    "overlap_jaccard": overlap_jaccard,
                }
            )

            directional_candidate = metric_record(
                score=forward_score,
                partner_id=target_relation_id,
                partner_name=relation_names[target_relation_id],
                overlap_count=overlap_count,
                forward_score=forward_score,
                backward_score=backward_score,
                jaccard=overlap_jaccard,
            )
            if is_better_candidate(directional_candidate, best_directional):
                best_directional = directional_candidate

            mutual_candidate = metric_record(
                score=mutual_score,
                partner_id=target_relation_id,
                partner_name=relation_names[target_relation_id],
                overlap_count=overlap_count,
                forward_score=forward_score,
                backward_score=backward_score,
                jaccard=overlap_jaccard,
            )
            if is_better_candidate(mutual_candidate, best_mutual):
                second_best_mutual = best_mutual
                best_mutual = mutual_candidate
            elif is_better_candidate(mutual_candidate, second_best_mutual):
                second_best_mutual = mutual_candidate

        best_directional = finalize_record(best_directional)
        best_mutual = finalize_record(best_mutual)
        second_best_mutual = finalize_record(second_best_mutual)
        inverse_clarity = max(0.0, best_mutual["score"] - second_best_mutual["score"])

        relation_rows.append(
            {
                "relation_id": source_relation_id,
                "relation_name": relation_names[source_relation_id],
                "train_support": source_support,
                "directional_inverse_strength": best_directional["score"],
                "directional_best_inverse_partner_id": best_directional["partner_id"],
                "directional_best_inverse_partner_name": best_directional["partner_name"],
                "directional_best_inverse_overlap_count": best_directional["overlap_count"],
                "directional_best_reverse_directional_score": best_directional[
                    "backward_score"
                ],
                "directional_best_overlap_jaccard": best_directional["jaccard"],
                "mutual_inverse_strength": best_mutual["score"],
                "mutual_best_inverse_partner_id": best_mutual["partner_id"],
                "mutual_best_inverse_partner_name": best_mutual["partner_name"],
                "mutual_best_inverse_overlap_count": best_mutual["overlap_count"],
                "mutual_best_directional_score": best_mutual["forward_score"],
                "mutual_best_reverse_directional_score": best_mutual["backward_score"],
                "mutual_best_overlap_jaccard": best_mutual["jaccard"],
                "second_best_mutual_inverse_strength": second_best_mutual["score"],
                "second_best_mutual_partner_id": second_best_mutual["partner_id"],
                "second_best_mutual_partner_name": second_best_mutual["partner_name"],
                "inverse_clarity": inverse_clarity,
            }
        )

    return relation_rows, pair_rows


def summarize_relation_rows(rows):
    directional_values = [row["directional_inverse_strength"] for row in rows]
    mutual_values = [row["mutual_inverse_strength"] for row in rows]
    clarity_values = [row["inverse_clarity"] for row in rows]

    lines = [
        "Inverse V2 Relation Stats Summary",
        "",
        f"Relations: {len(rows)}",
        (
            "Directional zero count: "
            f"{sum(value == 0.0 for value in directional_values)}"
        ),
        (
            "Mutual zero count: "
            f"{sum(value == 0.0 for value in mutual_values)}"
        ),
        (
            "Clarity zero count: "
            f"{sum(value == 0.0 for value in clarity_values)}"
        ),
        "",
    ]

    for label, values in [
        ("directional_inverse_strength", directional_values),
        ("mutual_inverse_strength", mutual_values),
        ("inverse_clarity", clarity_values),
    ]:
        sorted_values = sorted(values)
        lines.append(f"{label}:")
        lines.append(f"- min: {sorted_values[0]:.4f}")
        lines.append(f"- median: {sorted_values[len(sorted_values) // 2]:.4f}")
        lines.append(f"- max: {sorted_values[-1]:.4f}")
        lines.append("")

    return lines


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
    relation_output = os.path.join(args.output_dir, "relation_inverse_stats_v2.csv")
    pair_output = os.path.join(args.output_dir, "relation_inverse_pair_scores_v2.csv")
    summary_output = os.path.join(args.output_dir, "relation_inverse_stats_summary_v2.txt")

    write_csv(relation_output, relation_rows)
    write_csv(pair_output, pair_rows)
    with open(summary_output, "w") as f:
        f.write("\n".join(summarize_relation_rows(relation_rows)).rstrip() + "\n")

    print(f"Saved relation-level inverse v2 stats to: {relation_output}")
    print(f"Saved pair-level inverse v2 scores to: {pair_output}")
    print(f"Saved inverse v2 summary to: {summary_output}")


if __name__ == "__main__":
    main()
