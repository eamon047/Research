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


DEFAULT_INVERSE_CSV = "results/RotatE_FB15k237/inverse_v2/relation_inverse_stats_v2.csv"
DEFAULT_MULTIPLICITY_CSV = (
    "results/RotatE_FB15k237/mapping_type/combined/"
    "relation_metrics_num7_agg7_k10.csv"
)
DEFAULT_OUTPUT_DIR = "results/RotatE_FB15k237/inverse_v2"
DEFAULT_THRESHOLDS = [0, 5, 10]


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Merge inverse v2 statistics with relation-level multiplicity results "
            "and compute correlation and bucket summaries."
        )
    )
    parser.add_argument(
        "--inverse-csv",
        default=DEFAULT_INVERSE_CSV,
        help="Relation-level inverse v2 statistics CSV",
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

        merged_row = {
            "relation_id": relation_id,
            "relation_name": inverse_row["relation_name"],
            "mapping_type": multiplicity_row["mapping_type"],
            "train_support": inverse_row["train_support"],
            "test_support": multiplicity_row["test_support"],
            "head_support": multiplicity_row["head_support"],
            "tail_support": multiplicity_row["tail_support"],
            "eligible_support": multiplicity_row["eligible_support"],
            "hits_r": multiplicity_row["hits_r"],
            "alpha_r": multiplicity_row["alpha_r"],
            "delta_r": multiplicity_row["delta_r"],
        }

        for key in inverse_row:
            if key in {"relation_id", "relation_name", "train_support"}:
                continue
            merged_row[key] = inverse_row[key]

        merged_rows.append(merged_row)

    merged_rows.sort(key=lambda row: int(row["relation_id"]))
    return merged_rows


def filter_metric_rows(rows, threshold, inverse_metric, prediction_metric):
    filtered = []
    for row in rows:
        if as_int(row, "test_support") < threshold:
            continue
        inverse_value = as_float(row, inverse_metric)
        prediction_value = as_float(row, prediction_metric)
        if math.isnan(inverse_value) or math.isnan(prediction_value):
            continue
        filtered.append(row)
    return filtered


def correlation_rows(rows, thresholds):
    output_rows = []
    for threshold in thresholds:
        for inverse_metric in INVERSE_METRICS:
            for prediction_metric in PREDICTION_METRICS:
                filtered = filter_metric_rows(
                    rows, threshold, inverse_metric, prediction_metric
                )
                xs = [as_float(row, inverse_metric) for row in filtered]
                ys = [as_float(row, prediction_metric) for row in filtered]
                output_rows.append(
                    {
                        "threshold": threshold,
                        "inverse_metric": inverse_metric,
                        "prediction_metric": prediction_metric,
                        "n": len(filtered),
                        "spearman_rho": spearman_correlation(xs, ys),
                    }
                )
    return output_rows


def bucket_rows(rows, thresholds):
    output_rows = []
    for threshold in thresholds:
        threshold_rows = [row for row in rows if as_int(row, "test_support") >= threshold]
        for inverse_metric in INVERSE_METRICS:
            by_bucket = {label: [] for label in BUCKET_LABELS}
            for row in threshold_rows:
                inverse_value = as_float(row, inverse_metric)
                if math.isnan(inverse_value):
                    continue
                by_bucket[strength_bucket(inverse_value)].append(row)

            for bucket_label in BUCKET_LABELS:
                bucket_members = by_bucket[bucket_label]
                if not bucket_members:
                    continue

                row_data = {
                    "threshold": threshold,
                    "inverse_metric": inverse_metric,
                    "bucket": bucket_label,
                    "n": len(bucket_members),
                    "inverse_metric_mean": summarize_values(
                        [as_float(row, inverse_metric) for row in bucket_members]
                    )["mean"],
                    "test_support_mean": summarize_values(
                        [as_int(row, "test_support") for row in bucket_members]
                    )["mean"],
                    "train_support_mean": summarize_values(
                        [as_int(row, "train_support") for row in bucket_members]
                    )["mean"],
                }

                for prediction_metric in PREDICTION_METRICS:
                    values = [
                        as_float(row, prediction_metric)
                        for row in bucket_members
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
    lines = ["Inverse V2 Analysis Summary", "", f"Merged relations: {len(rows)}", ""]

    for inverse_metric in INVERSE_METRICS:
        lines.append(f"{inverse_metric}:")
        lines.append(
            f"- zero count: {sum(as_float(row, inverse_metric) == 0.0 for row in rows)}"
        )
        lines.append("")

    for threshold in thresholds:
        kept_rows = [row for row in rows if as_int(row, "test_support") >= threshold]
        lines.append(f"Threshold: test_support >= {threshold}")
        lines.append(f"Relations kept: {len(kept_rows)} / {len(rows)}")

        for inverse_metric in INVERSE_METRICS:
            lines.append(f"{inverse_metric}:")
            for prediction_metric in PREDICTION_METRICS:
                corr_row = next(
                    row
                    for row in correlation_stats
                    if row["threshold"] == threshold
                    and row["inverse_metric"] == inverse_metric
                    and row["prediction_metric"] == prediction_metric
                )
                rho = corr_row["spearman_rho"]
                rho_text = "nan" if math.isnan(rho) else f"{rho:.4f}"
                lines.append(
                    f"- Spearman({inverse_metric}, {prediction_metric}) = {rho_text} "
                    f"(n={corr_row['n']})"
                )
            lines.append("  Bucket means:")
            metric_bucket_rows = [
                row
                for row in bucket_stats
                if row["threshold"] == threshold and row["inverse_metric"] == inverse_metric
            ]
            for bucket_label in BUCKET_LABELS:
                bucket_row = next(
                    (row for row in metric_bucket_rows if row["bucket"] == bucket_label),
                    None,
                )
                if bucket_row is None:
                    continue
                lines.append(
                    f"  - {bucket_label}: n={bucket_row['n']}, "
                    f"metric_mean={bucket_row['inverse_metric_mean']:.4f}, "
                    f"hits_mean={bucket_row['hits_r_mean']:.4f}, "
                    f"alpha_mean={bucket_row['alpha_r_mean']:.4f}, "
                    f"delta_mean={bucket_row['delta_r_mean']:.4f}"
                )
            lines.append("")
        lines.append("")

    return lines


def main():
    args = parse_args()
    inverse_rows = load_rows(args.inverse_csv)
    multiplicity_rows = load_rows(args.multiplicity_csv)
    merged_rows = merge_rows(inverse_rows, multiplicity_rows)

    os.makedirs(args.output_dir, exist_ok=True)

    merged_output = os.path.join(
        args.output_dir, "relation_inverse_multiplicity_merged_v2.csv"
    )
    correlation_output = os.path.join(args.output_dir, "correlation_stats_v2.csv")
    bucket_output = os.path.join(args.output_dir, "bucket_stats_v2.csv")
    summary_output = os.path.join(args.output_dir, "analysis_summary_v2.txt")

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

    print(f"Saved merged v2 table to: {merged_output}")
    print(f"Saved v2 correlation stats to: {correlation_output}")
    print(f"Saved v2 bucket stats to: {bucket_output}")
    print(f"Saved v2 text summary to: {summary_output}")


if __name__ == "__main__":
    main()
