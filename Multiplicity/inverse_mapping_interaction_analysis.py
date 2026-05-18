import argparse
import csv
import math
import os


DEFAULT_INPUT_CSV = (
    "results/RotatE_FB15k237/inverse/relation_inverse_multiplicity_merged.csv"
)
DEFAULT_OUTPUT_DIR = "results/RotatE_FB15k237/inverse/mapping_interaction"
DEFAULT_THRESHOLDS = [5, 10]
METRICS = ["hits_r", "alpha_r", "delta_r"]
BUCKET_LABELS = ["zero", "(0,0.1]", "(0.1,0.3]", "(0.3,0.5]", "(0.5,1.0]"]


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Analyze inverse-strength and multiplicity relationships within each "
            "mapping type."
        )
    )
    parser.add_argument(
        "--input-csv",
        default=DEFAULT_INPUT_CSV,
        help="Merged inverse + multiplicity CSV",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
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
        rows = list(csv.DictReader(f))
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


def average_ranks(values):
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def pearson_correlation(xs, ys):
    if len(xs) != len(ys):
        raise ValueError("Lengths do not match")
    if len(xs) < 2:
        return math.nan
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = 0.0
    sum_sq_x = 0.0
    sum_sq_y = 0.0
    for x, y in zip(xs, ys):
        dx = x - mean_x
        dy = y - mean_y
        numerator += dx * dy
        sum_sq_x += dx * dx
        sum_sq_y += dy * dy
    denominator = math.sqrt(sum_sq_x * sum_sq_y)
    if denominator == 0.0:
        return math.nan
    return numerator / denominator


def spearman_correlation(xs, ys):
    if len(xs) < 2:
        return math.nan
    return pearson_correlation(average_ranks(xs), average_ranks(ys))


def inverse_bucket(value):
    if value == 0.0:
        return "zero"
    if value <= 0.1:
        return "(0,0.1]"
    if value <= 0.3:
        return "(0.1,0.3]"
    if value <= 0.5:
        return "(0.3,0.5]"
    return "(0.5,1.0]"


def write_csv(path, rows):
    if not rows:
        return
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def correlation_rows(rows, thresholds):
    output_rows = []
    mapping_types = sorted({row["mapping_type"] for row in rows})
    for threshold in thresholds:
        threshold_rows = [row for row in rows if as_int(row, "test_support") >= threshold]
        for mapping_type in mapping_types:
            mapping_rows = [row for row in threshold_rows if row["mapping_type"] == mapping_type]
            for metric in METRICS:
                filtered = [
                    row
                    for row in mapping_rows
                    if not math.isnan(as_float(row, "inverse_strength"))
                    and not math.isnan(as_float(row, metric))
                ]
                xs = [as_float(row, "inverse_strength") for row in filtered]
                ys = [as_float(row, metric) for row in filtered]
                output_rows.append(
                    {
                        "threshold": threshold,
                        "mapping_type": mapping_type,
                        "metric": metric,
                        "n": len(filtered),
                        "spearman_rho": spearman_correlation(xs, ys),
                    }
                )
    return output_rows


def bucket_rows(rows, thresholds):
    output_rows = []
    mapping_types = sorted({row["mapping_type"] for row in rows})
    for threshold in thresholds:
        threshold_rows = [row for row in rows if as_int(row, "test_support") >= threshold]
        for mapping_type in mapping_types:
            mapping_rows = [row for row in threshold_rows if row["mapping_type"] == mapping_type]
            by_bucket = {label: [] for label in BUCKET_LABELS}
            for row in mapping_rows:
                inv = as_float(row, "inverse_strength")
                if math.isnan(inv):
                    continue
                by_bucket[inverse_bucket(inv)].append(row)
            for bucket_label in BUCKET_LABELS:
                members = by_bucket[bucket_label]
                if not members:
                    continue
                row_data = {
                    "threshold": threshold,
                    "mapping_type": mapping_type,
                    "bucket": bucket_label,
                    "n": len(members),
                    "inverse_strength_mean": summarize_values(
                        [as_float(row, "inverse_strength") for row in members]
                    )["mean"],
                    "test_support_mean": summarize_values(
                        [as_int(row, "test_support") for row in members]
                    )["mean"],
                }
                for metric in METRICS:
                    values = [
                        as_float(row, metric)
                        for row in members
                        if not math.isnan(as_float(row, metric))
                    ]
                    if values:
                        summary = summarize_values(values)
                        row_data[f"{metric}_mean"] = summary["mean"]
                        row_data[f"{metric}_median"] = summary["median"]
                    else:
                        row_data[f"{metric}_mean"] = math.nan
                        row_data[f"{metric}_median"] = math.nan
                output_rows.append(row_data)
    return output_rows


def build_summary_lines(rows, correlation_stats, bucket_stats, thresholds):
    lines = []
    mapping_types = sorted({row["mapping_type"] for row in rows})
    lines.append("Inverse x Mapping-Type Interaction Summary")
    lines.append("")
    for threshold in thresholds:
        threshold_rows = [row for row in rows if as_int(row, "test_support") >= threshold]
        lines.append(f"Threshold: test_support >= {threshold}")
        lines.append(f"Rows kept: {len(threshold_rows)} / {len(rows)}")
        for mapping_type in mapping_types:
            kept = [row for row in threshold_rows if row["mapping_type"] == mapping_type]
            lines.append(f"Mapping type: {mapping_type} (n={len(kept)})")
            for metric in METRICS:
                corr_row = next(
                    row
                    for row in correlation_stats
                    if row["threshold"] == threshold
                    and row["mapping_type"] == mapping_type
                    and row["metric"] == metric
                )
                rho = corr_row["spearman_rho"]
                rho_text = "nan" if math.isnan(rho) else f"{rho:.4f}"
                lines.append(
                    f"- Spearman(inverse_strength, {metric}) = {rho_text} "
                    f"(n={corr_row['n']})"
                )
            lines.append("  Bucket means:")
            bucket_subset = [
                row
                for row in bucket_stats
                if row["threshold"] == threshold and row["mapping_type"] == mapping_type
            ]
            for bucket_label in BUCKET_LABELS:
                bucket_row = next(
                    (row for row in bucket_subset if row["bucket"] == bucket_label),
                    None,
                )
                if bucket_row is None:
                    continue
                lines.append(
                    f"  - {bucket_label}: n={bucket_row['n']}, "
                    f"hits_mean={bucket_row['hits_r_mean']:.4f}, "
                    f"alpha_mean={bucket_row['alpha_r_mean']:.4f}, "
                    f"delta_mean={bucket_row['delta_r_mean']:.4f}"
                )
            lines.append("")
        lines.append("")
    return lines


def main():
    args = parse_args()
    rows = load_rows(args.input_csv)
    os.makedirs(args.output_dir, exist_ok=True)

    correlation_stats = correlation_rows(rows, args.thresholds)
    bucket_stats = bucket_rows(rows, args.thresholds)
    summary_lines = build_summary_lines(rows, correlation_stats, bucket_stats, args.thresholds)

    correlation_output = os.path.join(args.output_dir, "correlation_by_mapping_type.csv")
    bucket_output = os.path.join(args.output_dir, "bucket_stats_by_mapping_type.csv")
    summary_output = os.path.join(args.output_dir, "summary.txt")

    write_csv(correlation_output, correlation_stats)
    write_csv(bucket_output, bucket_stats)
    with open(summary_output, "w") as f:
        f.write("\n".join(summary_lines).rstrip() + "\n")

    print(f"Saved correlation stats to: {correlation_output}")
    print(f"Saved bucket stats to: {bucket_output}")
    print(f"Saved text summary to: {summary_output}")


if __name__ == "__main__":
    main()
