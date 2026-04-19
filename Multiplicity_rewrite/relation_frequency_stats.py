import argparse
import math
import os

from kge import Config
from kge import Dataset
from kge.util.seed import seed_from_config

from relation_frequency_utils import summarize_values, write_csv


DEFAULT_EXPERIMENTS_ROOT = "LibKGE/local/multiplicity"
DEFAULT_EXPERIMENT_NAME = "RotatE_FB15k237"
DEFAULT_OUTPUT_DIR = "results/RotatE_FB15k237/relation_frequency"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute relation-level frequency statistics from the training graph."
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
        help="Directory for relation-frequency outputs",
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


def compute_frequency_rows(dataset):
    relation_names = list(dataset.relation_ids())
    train_triples = dataset.split("train")
    relation_counts = train_triples[:, 1].bincount(minlength=dataset.num_relations())

    rows = []
    for relation_id in range(dataset.num_relations()):
        train_frequency = int(relation_counts[relation_id].item())
        rows.append(
            {
                "relation_id": relation_id,
                "relation_name": relation_names[relation_id],
                "train_frequency": train_frequency,
                "log_train_frequency": math.log1p(train_frequency),
            }
        )
    return rows


def build_summary_lines(rows):
    frequency_values = [row["train_frequency"] for row in rows]
    log_values = [row["log_train_frequency"] for row in rows]
    frequency_summary = summarize_values(frequency_values)
    log_summary = summarize_values(log_values)

    top_frequency_rows = sorted(
        rows,
        key=lambda row: (row["train_frequency"], row["relation_id"]),
        reverse=True,
    )[:10]
    low_frequency_rows = sorted(
        rows,
        key=lambda row: (row["train_frequency"], row["relation_id"]),
    )[:10]

    lines = [
        "Relation Frequency Summary",
        "",
        f"Relations: {len(rows)}",
        f"train_frequency = 0: {sum(value == 0 for value in frequency_values)}",
        "",
        "train_frequency:",
        f"- min: {frequency_summary['min']}",
        f"- p25: {frequency_summary['p25']:.4f}",
        f"- median: {frequency_summary['median']:.4f}",
        f"- p75: {frequency_summary['p75']:.4f}",
        f"- p90: {frequency_summary['p90']:.4f}",
        f"- max: {frequency_summary['max']}",
        "",
        "log_train_frequency:",
        f"- min: {log_summary['min']:.4f}",
        f"- p25: {log_summary['p25']:.4f}",
        f"- median: {log_summary['median']:.4f}",
        f"- p75: {log_summary['p75']:.4f}",
        f"- p90: {log_summary['p90']:.4f}",
        f"- max: {log_summary['max']:.4f}",
        "",
        "Highest-frequency relations:",
    ]

    for row in top_frequency_rows:
        lines.append(
            f"- {row['relation_name']}: train_frequency={row['train_frequency']}, "
            f"log_train_frequency={row['log_train_frequency']:.4f}"
        )

    lines.append("")
    lines.append("Lowest-frequency relations:")
    for row in low_frequency_rows:
        lines.append(
            f"- {row['relation_name']}: train_frequency={row['train_frequency']}, "
            f"log_train_frequency={row['log_train_frequency']:.4f}"
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
    rows = compute_frequency_rows(dataset)

    os.makedirs(args.output_dir, exist_ok=True)
    stats_output = os.path.join(args.output_dir, "relation_frequency_stats.csv")
    summary_output = os.path.join(args.output_dir, "frequency_summary.txt")

    write_csv(stats_output, rows)
    with open(summary_output, "w") as f:
        f.write("\n".join(build_summary_lines(rows)).rstrip() + "\n")

    print(f"Saved relation-level frequency stats to: {stats_output}")
    print(f"Saved relation-frequency summary to: {summary_output}")


if __name__ == "__main__":
    main()
