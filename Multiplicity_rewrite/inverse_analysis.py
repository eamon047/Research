import argparse
import csv
import math
import os


DEFAULT_INVERSE_CSV = "results/RotatE_FB15k237/inverse/relation_inverse_stats.csv"
DEFAULT_MULTIPLICITY_CSV = (
    "results/RotatE_FB15k237/mapping_type/combined/"
    "relation_metrics_num7_agg7_k10.csv"
)
DEFAULT_OUTPUT_DIR = "results/RotatE_FB15k237/inverse"
DEFAULT_THRESHOLDS = [0, 5, 10]
METRICS = ["hits_r", "alpha_r", "delta_r"]
BUCKET_LABELS = [
    "zero",
    "(0,0.1]",
    "(0.1,0.3]",
    "(0.3,0.5]",
    "(0.5,1.0]",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Merge inverse statistics with relation-level multiplicity results and "
            "compute correlation and bucket summaries."
        )
    )
    parser.add_argument(
        "--inverse-csv",
        default=DEFAULT_INVERSE_CSV,
        help="Relation-level inverse statistics CSV",
    )
    parser.add_argument(
        "--multiplicity-csv",
        default=DEFAULT_MULTIPLICITY_CSV,
        help="Combined relation-level multiplicity CSV",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for merged outputs and summaries",
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


def merge_rows(inverse_rows, multiplicity_rows):
    multiplicity_by_relation = {row["relation_id"]: row for row in multiplicity_rows}
    merged_rows = []

    for inverse_row in inverse_rows:
        relation_id = inverse_row["relation_id"]
        if relation_id not in multiplicity_by_relation:
            raise KeyError(f"Relation {relation_id} missing from multiplicity table")

        multiplicity_row = multiplicity_by_relation[relation_id]
        if inverse_row["relation_name"] != multiplicity_row["relation_name"]:
            raise ValueError(
                "Relation name mismatch for relation_id "
                f"{relation_id}: {inverse_row['relation_name']} vs "
                f"{multiplicity_row['relation_name']}"
            )

        merged_rows.append(
            {
                "relation_id": relation_id,
                "relation_name": inverse_row["relation_name"],
                "mapping_type": multiplicity_row["mapping_type"],
                "train_support": inverse_row["train_support"],
                "test_support": multiplicity_row["test_support"],
                "head_support": multiplicity_row["head_support"],
                "tail_support": multiplicity_row["tail_support"],
                "eligible_support": multiplicity_row["eligible_support"],
                "inverse_strength": inverse_row["inverse_strength"],
                "best_inverse_partner_id": inverse_row["best_inverse_partner_id"],
                "best_inverse_partner_name": inverse_row["best_inverse_partner_name"],
                "best_inverse_score": inverse_row["best_inverse_score"],
                "best_inverse_overlap_count": inverse_row["best_inverse_overlap_count"],
                "hits_r": multiplicity_row["hits_r"],
                "alpha_r": multiplicity_row["alpha_r"],
                "delta_r": multiplicity_row["delta_r"],
            }
        )

    merged_rows.sort(key=lambda row: int(row["relation_id"]))
    return merged_rows


def write_csv(path, rows):
    if not rows:
        return
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


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


def filter_metric_rows(rows, threshold, metric):
    filtered = []
    for row in rows:
        if as_int(row, "test_support") < threshold:
            continue
        metric_value = as_float(row, metric)
        inverse_strength = as_float(row, "inverse_strength")
        if math.isnan(metric_value) or math.isnan(inverse_strength):
            continue
        filtered.append(row)
    return filtered


def correlation_rows(rows, thresholds):
    output_rows = []
    for threshold in thresholds:
        for metric in METRICS:
            filtered = filter_metric_rows(rows, threshold, metric)
            xs = [as_float(row, "inverse_strength") for row in filtered]
            ys = [as_float(row, metric) for row in filtered]
            output_rows.append(
                {
                    "threshold": threshold,
                    "metric": metric,
                    "n": len(filtered),
                    "spearman_rho": spearman_correlation(xs, ys),
                }
            )
    return output_rows


def bucket_rows(rows, thresholds):
    output_rows = []
    for threshold in thresholds:
        threshold_rows = [
            row
            for row in rows
            if as_int(row, "test_support") >= threshold
            and not math.isnan(as_float(row, "inverse_strength"))
        ]
        by_bucket = {label: [] for label in BUCKET_LABELS}
        for row in threshold_rows:
            by_bucket[inverse_bucket(as_float(row, "inverse_strength"))].append(row)

        for bucket_label in BUCKET_LABELS:
            bucket_members = by_bucket[bucket_label]
            if not bucket_members:
                continue

            row_data = {
                "threshold": threshold,
                "bucket": bucket_label,
                "n": len(bucket_members),
                "inverse_strength_mean": summarize_values(
                    [as_float(row, "inverse_strength") for row in bucket_members]
                )["mean"],
                "test_support_mean": summarize_values(
                    [as_int(row, "test_support") for row in bucket_members]
                )["mean"],
                "train_support_mean": summarize_values(
                    [as_int(row, "train_support") for row in bucket_members]
                )["mean"],
            }

            for metric in METRICS:
                values = [
                    as_float(row, metric)
                    for row in bucket_members
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
    lines.append("Inverse Analysis Summary")
    lines.append("")
    lines.append(f"Merged relations: {len(rows)}")
    lines.append(
        f"Relations with inverse_strength = 0: "
        f"{sum(as_float(row, 'inverse_strength') == 0.0 for row in rows)}"
    )
    lines.append("")

    for threshold in thresholds:
        kept_rows = [row for row in rows if as_int(row, "test_support") >= threshold]
        lines.append(f"Threshold: test_support >= {threshold}")
        lines.append(f"Relations kept: {len(kept_rows)} / {len(rows)}")

        for metric in METRICS:
            corr_row = next(
                row
                for row in correlation_stats
                if row["threshold"] == threshold and row["metric"] == metric
            )
            rho = corr_row["spearman_rho"]
            rho_text = "nan" if math.isnan(rho) else f"{rho:.4f}"
            lines.append(
                f"- Spearman(inverse_strength, {metric}) = {rho_text} "
                f"(n={corr_row['n']})"
            )

        lines.append("")
        lines.append("Bucket means:")
        threshold_bucket_rows = [
            row for row in bucket_stats if row["threshold"] == threshold
        ]
        for bucket_label in BUCKET_LABELS:
            bucket_row = next(
                (row for row in threshold_bucket_rows if row["bucket"] == bucket_label),
                None,
            )
            if bucket_row is None:
                continue
            lines.append(
                f"- {bucket_label}: n={bucket_row['n']}, "
                f"inverse_mean={bucket_row['inverse_strength_mean']:.4f}, "
                f"hits_mean={bucket_row['hits_r_mean']:.4f}, "
                f"alpha_mean={bucket_row['alpha_r_mean']:.4f}, "
                f"delta_mean={bucket_row['delta_r_mean']:.4f}"
            )
        lines.append("")

    return lines


def main():
    args = parse_args()
    inverse_rows = load_rows(args.inverse_csv)
    multiplicity_rows = load_rows(args.multiplicity_csv)
    merged_rows = merge_rows(inverse_rows, multiplicity_rows)

    os.makedirs(args.output_dir, exist_ok=True)

    merged_output = os.path.join(
        args.output_dir, "relation_inverse_multiplicity_merged.csv"
    )
    correlation_output = os.path.join(args.output_dir, "correlation_stats.csv")
    bucket_output = os.path.join(args.output_dir, "bucket_stats.csv")
    summary_output = os.path.join(args.output_dir, "analysis_summary.txt")

    correlation_stats = correlation_rows(merged_rows, args.thresholds)
    bucket_stats = bucket_rows(merged_rows, args.thresholds)
    summary_lines = build_summary_lines(
        merged_rows, correlation_stats, bucket_stats, args.thresholds
    )

    write_csv(merged_output, merged_rows)
    write_csv(correlation_output, correlation_stats)
    write_csv(bucket_output, bucket_stats)
    with open(summary_output, "w") as f:
        f.write("\n".join(summary_lines).rstrip() + "\n")

    print(f"Saved merged table to: {merged_output}")
    print(f"Saved correlation stats to: {correlation_output}")
    print(f"Saved bucket stats to: {bucket_output}")
    print(f"Saved text summary to: {summary_output}")


if __name__ == "__main__":
    main()
