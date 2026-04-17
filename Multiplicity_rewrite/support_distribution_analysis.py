import argparse
import csv
import math
import os
from collections import Counter, defaultdict


DEFAULT_THRESHOLDS = [1, 2, 3, 5, 10, 15, 20, 30, 40, 50]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze support distributions for relation-level multiplicity CSV."
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
        help="Candidate minimum-support thresholds to evaluate",
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


def summarize_numeric(values):
    sorted_values = sorted(values)
    return {
        "min": sorted_values[0],
        "p25": percentile(sorted_values, 0.25),
        "median": percentile(sorted_values, 0.5),
        "p75": percentile(sorted_values, 0.75),
        "p90": percentile(sorted_values, 0.9),
        "max": sorted_values[-1],
        "mean": sum(sorted_values) / len(sorted_values),
    }


def format_summary_line(name, summary):
    return (
        f"{name}: min={summary['min']}, p25={summary['p25']:.2f}, "
        f"median={summary['median']:.2f}, p75={summary['p75']:.2f}, "
        f"p90={summary['p90']:.2f}, max={summary['max']}, mean={summary['mean']:.2f}"
    )


def build_threshold_rows(rows, thresholds):
    mapping_types = sorted({row["mapping_type"] for row in rows})
    threshold_rows = []
    for threshold in thresholds:
        kept_rows = [row for row in rows if as_int(row, "test_support") >= threshold]
        threshold_row = {
            "threshold": threshold,
            "relations_kept": len(kept_rows),
            "relations_dropped": len(rows) - len(kept_rows),
        }
        for mapping_type in mapping_types:
            threshold_row[f"kept_{mapping_type}"] = sum(
                1 for row in kept_rows if row["mapping_type"] == mapping_type
            )
        threshold_rows.append(threshold_row)
    return threshold_rows


def write_threshold_csv(path, threshold_rows):
    if not threshold_rows:
        return
    fieldnames = list(threshold_rows[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(threshold_rows)


def write_text_summary(path, rows, thresholds, test_summary, eligible_summary):
    mapping_counts = Counter(row["mapping_type"] for row in rows)
    zero_eligible = sum(1 for row in rows if as_int(row, "eligible_support") == 0)
    threshold_rows = build_threshold_rows(rows, thresholds)

    lines = []
    lines.append("Relation-level support analysis")
    lines.append("")
    lines.append(f"Input rows: {len(rows)}")
    lines.append("Mapping type counts:")
    for mapping_type, count in sorted(mapping_counts.items()):
        lines.append(f"- {mapping_type}: {count}")
    lines.append("")
    lines.append(format_summary_line("test_support", test_summary))
    lines.append(format_summary_line("eligible_support", eligible_summary))
    lines.append(f"eligible_support == 0: {zero_eligible}")
    lines.append("")
    lines.append(
        "Note: eligible_support counts relation-specific head/tail queries that satisfy "
        "'at least one output hits@k'. It is computed on combined query instances, so "
        "its natural upper bound is head_support + tail_support."
    )
    lines.append("")
    lines.append("Threshold sensitivity (minimum test_support):")
    for row in threshold_rows:
        line = (
            f"- >= {row['threshold']}: keep {row['relations_kept']} / {len(rows)} "
            f"relations, drop {row['relations_dropped']}"
        )
        for key in sorted(k for k in row.keys() if k.startswith("kept_")):
            line += f", {key}={row[key]}"
        lines.append(line)

    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    args = parse_args()
    rows = load_rows(args.input_csv)

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    test_support_values = [as_int(row, "test_support") for row in rows]
    eligible_support_values = [as_int(row, "eligible_support") for row in rows]

    test_summary = summarize_numeric(test_support_values)
    eligible_summary = summarize_numeric(eligible_support_values)
    threshold_rows = build_threshold_rows(rows, args.thresholds)

    summary_txt = os.path.join(output_dir, "support_summary.txt")
    threshold_csv = os.path.join(output_dir, "test_support_thresholds.csv")

    write_text_summary(
        summary_txt,
        rows,
        args.thresholds,
        test_summary,
        eligible_summary,
    )
    write_threshold_csv(threshold_csv, threshold_rows)

    print(f"Saved text summary to: {summary_txt}")
    print(f"Saved threshold table to: {threshold_csv}")


if __name__ == "__main__":
    main()
