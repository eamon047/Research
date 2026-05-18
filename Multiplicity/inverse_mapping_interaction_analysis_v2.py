import argparse
import math
import os

from inverse_v2_utils import (
    BUCKET_LABELS,
    INVERSE_METRICS,
    PREDICTION_METRICS,
    as_float,
    as_int,
    load_rows,
    spearman_correlation,
    strength_bucket,
    summarize_values,
    write_csv,
)


DEFAULT_INPUT_CSV = (
    "results/RotatE_FB15k237/inverse_v2/relation_inverse_multiplicity_merged_v2.csv"
)
DEFAULT_OUTPUT_DIR = "results/RotatE_FB15k237/inverse_v2/mapping_interaction"
DEFAULT_THRESHOLDS = [5, 10]


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Analyze inverse v2 metrics and multiplicity relationships within each "
            "mapping type."
        )
    )
    parser.add_argument(
        "--input-csv",
        default=DEFAULT_INPUT_CSV,
        help="Merged inverse v2 + multiplicity CSV",
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


def correlation_rows(rows, thresholds):
    output_rows = []
    mapping_types = sorted({row["mapping_type"] for row in rows})
    for threshold in thresholds:
        threshold_rows = [row for row in rows if as_int(row, "test_support") >= threshold]
        for mapping_type in mapping_types:
            mapping_rows = [row for row in threshold_rows if row["mapping_type"] == mapping_type]
            for inverse_metric in INVERSE_METRICS:
                for prediction_metric in PREDICTION_METRICS:
                    filtered = [
                        row
                        for row in mapping_rows
                        if not math.isnan(as_float(row, inverse_metric))
                        and not math.isnan(as_float(row, prediction_metric))
                    ]
                    xs = [as_float(row, inverse_metric) for row in filtered]
                    ys = [as_float(row, prediction_metric) for row in filtered]
                    output_rows.append(
                        {
                            "threshold": threshold,
                            "mapping_type": mapping_type,
                            "inverse_metric": inverse_metric,
                            "prediction_metric": prediction_metric,
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
            for inverse_metric in INVERSE_METRICS:
                by_bucket = {label: [] for label in BUCKET_LABELS}
                for row in mapping_rows:
                    inverse_value = as_float(row, inverse_metric)
                    if math.isnan(inverse_value):
                        continue
                    by_bucket[strength_bucket(inverse_value)].append(row)

                for bucket_label in BUCKET_LABELS:
                    members = by_bucket[bucket_label]
                    if not members:
                        continue
                    row_data = {
                        "threshold": threshold,
                        "mapping_type": mapping_type,
                        "inverse_metric": inverse_metric,
                        "bucket": bucket_label,
                        "n": len(members),
                        "inverse_metric_mean": summarize_values(
                            [as_float(row, inverse_metric) for row in members]
                        )["mean"],
                        "test_support_mean": summarize_values(
                            [as_int(row, "test_support") for row in members]
                        )["mean"],
                    }
                    for prediction_metric in PREDICTION_METRICS:
                        values = [
                            as_float(row, prediction_metric)
                            for row in members
                            if not math.isnan(as_float(row, prediction_metric))
                        ]
                        if values:
                            summary = summarize_values(values)
                            row_data[f"{prediction_metric}_mean"] = summary["mean"]
                            row_data[f"{prediction_metric}_median"] = summary["median"]
                        else:
                            row_data[f"{prediction_metric}_mean"] = math.nan
                            row_data[f"{prediction_metric}_median"] = math.nan
                    output_rows.append(row_data)
    return output_rows


def build_summary_lines(rows, correlation_stats, bucket_stats, thresholds):
    lines = ["Inverse V2 x Mapping-Type Interaction Summary", ""]
    mapping_types = sorted({row["mapping_type"] for row in rows})
    for threshold in thresholds:
        threshold_rows = [row for row in rows if as_int(row, "test_support") >= threshold]
        lines.append(f"Threshold: test_support >= {threshold}")
        lines.append(f"Rows kept: {len(threshold_rows)} / {len(rows)}")
        for mapping_type in mapping_types:
            kept = [row for row in threshold_rows if row["mapping_type"] == mapping_type]
            lines.append(f"Mapping type: {mapping_type} (n={len(kept)})")
            for inverse_metric in INVERSE_METRICS:
                lines.append(f"  {inverse_metric}:")
                for prediction_metric in PREDICTION_METRICS:
                    corr_row = next(
                        row
                        for row in correlation_stats
                        if row["threshold"] == threshold
                        and row["mapping_type"] == mapping_type
                        and row["inverse_metric"] == inverse_metric
                        and row["prediction_metric"] == prediction_metric
                    )
                    rho = corr_row["spearman_rho"]
                    rho_text = "nan" if math.isnan(rho) else f"{rho:.4f}"
                    lines.append(
                        f"  - Spearman({inverse_metric}, {prediction_metric}) = "
                        f"{rho_text} (n={corr_row['n']})"
                    )
                lines.append("    Bucket means:")
                bucket_subset = [
                    row
                    for row in bucket_stats
                    if row["threshold"] == threshold
                    and row["mapping_type"] == mapping_type
                    and row["inverse_metric"] == inverse_metric
                ]
                for bucket_label in BUCKET_LABELS:
                    bucket_row = next(
                        (row for row in bucket_subset if row["bucket"] == bucket_label),
                        None,
                    )
                    if bucket_row is None:
                        continue
                    lines.append(
                        f"    - {bucket_label}: n={bucket_row['n']}, "
                        f"hits_mean={bucket_row['hits_r_mean']:.4f}, "
                        f"alpha_mean={bucket_row['alpha_r_mean']:.4f}, "
                        f"delta_mean={bucket_row['delta_r_mean']:.4f}"
                    )
                lines.append("")
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

    correlation_output = os.path.join(args.output_dir, "correlation_by_mapping_type_v2.csv")
    bucket_output = os.path.join(args.output_dir, "bucket_stats_by_mapping_type_v2.csv")
    summary_output = os.path.join(args.output_dir, "summary_v2.txt")

    write_csv(correlation_output, correlation_stats)
    write_csv(bucket_output, bucket_stats)
    with open(summary_output, "w") as f:
        f.write("\n".join(summary_lines).rstrip() + "\n")

    print(f"Saved v2 correlation stats to: {correlation_output}")
    print(f"Saved v2 bucket stats to: {bucket_output}")
    print(f"Saved v2 text summary to: {summary_output}")


if __name__ == "__main__":
    main()
