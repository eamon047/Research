import argparse
import os

from kge import Config
from kge import Dataset
from kge.util.seed import seed_from_config

from symmetry_utils import summarize_values, write_csv


DEFAULT_EXPERIMENTS_ROOT = "LibKGE/local"
DEFAULT_EXPERIMENT_NAME = "RotatE_FB15k237"
DEFAULT_OUTPUT_DIR = "results/RotatE_FB15k237/symmetry"


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Compute relation-level symmetry statistics from the training graph."
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
        help="Directory for symmetry outputs",
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
    for head, relation, tail in train_triples.tolist():
        edge_sets[relation].add((head, tail))
    return edge_sets


def safe_ratio(numerator, denominator):
    if denominator == 0:
        return 0.0
    return numerator / denominator


def compute_symmetry_rows(dataset):
    relation_names = list(dataset.relation_ids())
    num_relations = dataset.num_relations()
    train_triples = dataset.split("train")
    edge_sets = build_relation_edge_sets(train_triples, num_relations)

    rows = []
    for relation_id in range(num_relations):
        edges = edge_sets[relation_id]
        train_support = len(edges)
        self_loop_count = sum(1 for head, tail in edges if head == tail)
        symmetric_supported_edge_count = sum(
            1 for head, tail in edges if (tail, head) in edges
        )
        non_self_train_support = train_support - self_loop_count
        symmetric_supported_non_self_edge_count = max(
            0, symmetric_supported_edge_count - self_loop_count
        )
        symmetry_score = safe_ratio(symmetric_supported_edge_count, train_support)
        symmetry_score_excluding_self_loops = safe_ratio(
            symmetric_supported_non_self_edge_count,
            non_self_train_support,
        )

        rows.append(
            {
                "relation_id": relation_id,
                "relation_name": relation_names[relation_id],
                "train_support": train_support,
                "self_loop_count": self_loop_count,
                "non_self_train_support": non_self_train_support,
                "symmetric_supported_edge_count": symmetric_supported_edge_count,
                "symmetric_supported_non_self_edge_count": (
                    symmetric_supported_non_self_edge_count
                ),
                "symmetry_score": symmetry_score,
                "symmetry_score_excluding_self_loops": (
                    symmetry_score_excluding_self_loops
                ),
            }
        )
    return rows


def build_summary_lines(rows):
    symmetry_values = [row["symmetry_score"] for row in rows]
    symmetry_excluding_self_values = [
        row["symmetry_score_excluding_self_loops"] for row in rows
    ]
    self_loop_counts = [row["self_loop_count"] for row in rows]
    self_loop_relations = sum(1 for value in self_loop_counts if value > 0)
    total_self_loops = sum(self_loop_counts)
    large_shift_relations = sum(
        1
        for row in rows
        if abs(
            row["symmetry_score"] - row["symmetry_score_excluding_self_loops"]
        )
        > 0.05
    )

    symmetry_summary = summarize_values(symmetry_values)
    symmetry_ex_summary = summarize_values(symmetry_excluding_self_values)

    top_high = sorted(
        rows,
        key=lambda row: (
            row["symmetry_score"],
            row["symmetric_supported_edge_count"],
            row["train_support"],
        ),
        reverse=True,
    )[:10]
    top_shift = sorted(
        rows,
        key=lambda row: abs(
            row["symmetry_score"] - row["symmetry_score_excluding_self_loops"]
        ),
        reverse=True,
    )[:10]

    lines = [
        "Symmetry Relation Stats Summary",
        "",
        f"Relations: {len(rows)}",
        f"symmetry_score = 0: {sum(value == 0.0 for value in symmetry_values)}",
        f"symmetry_score > 0.5: {sum(value > 0.5 for value in symmetry_values)}",
        (
            "Relations with self_loops > 0: "
            f"{self_loop_relations}"
        ),
        f"Total self loops: {total_self_loops}",
        (
            "Relations with |raw - excluding_self| > 0.05: "
            f"{large_shift_relations}"
        ),
        "",
        "symmetry_score:",
        f"- min: {symmetry_summary['min']:.4f}",
        f"- p25: {symmetry_summary['p25']:.4f}",
        f"- median: {symmetry_summary['median']:.4f}",
        f"- p75: {symmetry_summary['p75']:.4f}",
        f"- p90: {symmetry_summary['p90']:.4f}",
        f"- max: {symmetry_summary['max']:.4f}",
        "",
        "symmetry_score_excluding_self_loops:",
        f"- min: {symmetry_ex_summary['min']:.4f}",
        f"- p25: {symmetry_ex_summary['p25']:.4f}",
        f"- median: {symmetry_ex_summary['median']:.4f}",
        f"- p75: {symmetry_ex_summary['p75']:.4f}",
        f"- p90: {symmetry_ex_summary['p90']:.4f}",
        f"- max: {symmetry_ex_summary['max']:.4f}",
        "",
        "Top symmetry_score relations:",
    ]

    for row in top_high:
        lines.append(
            f"- {row['relation_name']}: symmetry={row['symmetry_score']:.4f}, "
            f"train_support={row['train_support']}, "
            f"symmetric_supported_edge_count={row['symmetric_supported_edge_count']}, "
            f"self_loop_count={row['self_loop_count']}"
        )

    lines.append("")
    lines.append("Largest self-loop sensitivity:")
    for row in top_shift:
        diff = abs(
            row["symmetry_score"] - row["symmetry_score_excluding_self_loops"]
        )
        lines.append(
            f"- {row['relation_name']}: diff={diff:.4f}, "
            f"raw={row['symmetry_score']:.4f}, "
            f"excluding_self={row['symmetry_score_excluding_self_loops']:.4f}, "
            f"self_loop_count={row['self_loop_count']}, "
            f"train_support={row['train_support']}"
        )

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
    rows = compute_symmetry_rows(dataset)

    os.makedirs(args.output_dir, exist_ok=True)
    stats_output = os.path.join(args.output_dir, "relation_symmetry_stats.csv")
    summary_output = os.path.join(args.output_dir, "symmetry_summary.txt")

    write_csv(stats_output, rows)
    with open(summary_output, "w") as f:
        f.write("\n".join(build_summary_lines(rows)).rstrip() + "\n")

    print(f"Saved relation-level symmetry stats to: {stats_output}")
    print(f"Saved symmetry summary to: {summary_output}")


if __name__ == "__main__":
    main()
