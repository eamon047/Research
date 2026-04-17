import argparse
import csv
import math
import os
from collections import defaultdict


DEFAULT_THRESHOLDS = [5, 10]
METRICS = ["hits_r", "alpha_r", "delta_r"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze relation-level multiplicity CSV by mapping type."
    )
    parser.add_argument(
        "--input-csv",
        default=(
            "results/RotatE_FB15k237/mapping_type/combined/"
            "relation_metrics_num7_agg7_k10.csv"
        ),
        help="Path to the relation-level CSV exported by relation_mapping_analysis.py",
    )
    parser.add_argument(
        "--output-dir",
        default="results/RotatE_FB15k237/mapping_type/combined",
        help="Directory for summary outputs",
    )
    parser.add_argument(
        "--thresholds",
        nargs="*",
        type=int,
        default=DEFAULT_THRESHOLDS,
        help="Minimum test_support thresholds to analyze",
    )
    return parser.parse_args()


def load_rows(path):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        raise ValueError(f"No rows found in {path}")
    return rows


def as_int(row, key):
    return int(row[key])


def as_float(row, key):
    value = row[key]
    if value == "" or value.lower() == "nan":
        return math.nan
    return float(value)


def percentile(sorted_values, p):
    if not sorted_values:
        return math.nan
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    position = (len(sorted_values) - 1) * p
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(sorted_values[lower])
    lower_value = sorted_values[lower]
    upper_value = sorted_values[upper]
    weight = position - lower
    return float(lower_value + (upper_value - lower_value) * weight)


def summarize_values(values):
    values = sorted(values)
    return {
        "n": len(values),
        "mean": sum(values) / len(values),
        "median": percentile(values, 0.5),
        "p25": percentile(values, 0.25),
        "p75": percentile(values, 0.75),
        "min": values[0],
        "max": values[-1],
    }


def format_summary(metric, mapping_type, summary):
    return (
        f"- {metric} | {mapping_type}: n={summary['n']}, mean={summary['mean']:.4f}, "
        f"median={summary['median']:.4f}, p25={summary['p25']:.4f}, "
        f"p75={summary['p75']:.4f}, min={summary['min']:.4f}, max={summary['max']:.4f}"
    )


def write_grouped_csv(path, grouped_rows):
    if not grouped_rows:
        return
    fieldnames = list(grouped_rows[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(grouped_rows)


def analyze_threshold(rows, threshold):
    kept_rows = [row for row in rows if as_int(row, "test_support") >= threshold]
    mapping_types = sorted({row["mapping_type"] for row in kept_rows})

    grouped_rows = []
    summary_lines = []
    summary_lines.append(f"Threshold: test_support >= {threshold}")
    summary_lines.append(f"Relations kept: {len(kept_rows)} / {len(rows)}")
    summary_lines.append("")

    for metric in METRICS:
        summary_lines.append(f"{metric}:")
        metric_summaries = []
        for mapping_type in mapping_types:
            values = [
                as_float(row, metric)
                for row in kept_rows
                if row["mapping_type"] == mapping_type and not math.isnan(as_float(row, metric))
            ]
            if not values:
                continue
            summary = summarize_values(values)
            metric_summaries.append((mapping_type, summary))
            grouped_rows.append(
                {
                    "threshold": threshold,
                    "metric": metric,
                    "mapping_type": mapping_type,
                    "n": summary["n"],
                    "mean": summary["mean"],
                    "median": summary["median"],
                    "p25": summary["p25"],
                    "p75": summary["p75"],
                    "min": summary["min"],
                    "max": summary["max"],
                }
            )
        metric_summaries.sort(key=lambda item: item[1]["mean"], reverse=True)
        for mapping_type, summary in metric_summaries:
            summary_lines.append(format_summary(metric, mapping_type, summary))
        if metric_summaries:
            top_type = metric_summaries[0][0]
            bottom_type = metric_summaries[-1][0]
            summary_lines.append(
                f"  mean ranking: highest={top_type}, lowest={bottom_type}"
            )
        summary_lines.append("")

    return kept_rows, grouped_rows, summary_lines


def main():
    args = parse_args()
    rows = load_rows(args.input_csv)
    os.makedirs(args.output_dir, exist_ok=True)

    all_grouped_rows = []
    all_lines = []

    for threshold in args.thresholds:
        _kept_rows, grouped_rows, summary_lines = analyze_threshold(rows, threshold)
        all_grouped_rows.extend(grouped_rows)
        all_lines.extend(summary_lines)
        all_lines.append("")

    summary_txt = os.path.join(args.output_dir, "mapping_type_summary.txt")
    summary_csv = os.path.join(args.output_dir, "mapping_type_grouped_stats.csv")

    with open(summary_txt, "w") as f:
        f.write("\n".join(all_lines).rstrip() + "\n")
    write_grouped_csv(summary_csv, all_grouped_rows)

    print(f"Saved text summary to: {summary_txt}")
    print(f"Saved grouped stats to: {summary_csv}")


if __name__ == "__main__":
    main()
