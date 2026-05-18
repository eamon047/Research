import argparse
import math
import os

from relation_frequency_utils import (
    FREQUENCY_BUCKET_LABELS,
    PREDICTION_METRICS,
    as_float,
    as_int,
    compute_frequency_bucket_bounds,
    frequency_bucket,
    load_rows,
    spearman_correlation,
    summarize_values,
    write_csv,
)


DEFAULT_FREQUENCY_CSV = (
    "results/RotatE_FB15k237/relation_frequency/relation_frequency_stats.csv"
)
DEFAULT_MULTIPLICITY_CSV = (
    "results/RotatE_FB15k237/mapping_type/combined/"
    "relation_metrics_num7_agg7_k10.csv"
)
DEFAULT_OUTPUT_DIR = "results/RotatE_FB15k237/relation_frequency"
DEFAULT_THRESHOLDS = [0, 5, 10]


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Merge relation-frequency statistics with relation-level multiplicity "
            "results and compute correlation and bucket summaries."
        )
    )
    parser.add_argument(
        "--frequency-csv",
        default=DEFAULT_FREQUENCY_CSV,
        help="Relation-level frequency statistics CSV",
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


def merge_rows(frequency_rows, multiplicity_rows):
    multiplicity_by_relation = {row["relation_id"]: row for row in multiplicity_rows}
    merged_rows = []

    for frequency_row in frequency_rows:
        relation_id = frequency_row["relation_id"]
        if relation_id not in multiplicity_by_relation:
            raise KeyError(f"Relation {relation_id} missing from multiplicity table")

        multiplicity_row = multiplicity_by_relation[relation_id]
        if frequency_row["relation_name"] != multiplicity_row["relation_name"]:
            raise ValueError(
                "Relation name mismatch for relation_id "
                f"{relation_id}: {frequency_row['relation_name']} vs "
                f"{multiplicity_row['relation_name']}"
            )

        merged_rows.append(
            {
                "relation_id": relation_id,
                "relation_name": frequency_row["relation_name"],
                "mapping_type": multiplicity_row["mapping_type"],
                "train_frequency": frequency_row["train_frequency"],
                "log_train_frequency": frequency_row["log_train_frequency"],
                "test_support": multiplicity_row["test_support"],
                "head_support": multiplicity_row["head_support"],
                "tail_support": multiplicity_row["tail_support"],
                "eligible_support": multiplicity_row["eligible_support"],
                "hits_r": multiplicity_row["hits_r"],
                "alpha_r": multiplicity_row["alpha_r"],
                "delta_r": multiplicity_row["delta_r"],
            }
        )

    merged_rows.sort(key=lambda row: int(row["relation_id"]))
    return merged_rows


def correlation_rows(rows, thresholds):
    output_rows = []
    for threshold in thresholds:
        threshold_rows = [row for row in rows if as_int(row, "test_support") >= threshold]
        for prediction_metric in PREDICTION_METRICS:
            filtered = [
                row
                for row in threshold_rows
                if not math.isnan(as_float(row, "log_train_frequency"))
                and not math.isnan(as_float(row, prediction_metric))
            ]
            xs = [as_float(row, "log_train_frequency") for row in filtered]
            ys = [as_float(row, prediction_metric) for row in filtered]
            output_rows.append(
                {
                    "threshold": threshold,
                    "prediction_metric": prediction_metric,
                    "n": len(filtered),
                    "spearman_rho": spearman_correlation(xs, ys),
                }
            )
    return output_rows


def bucket_rows(rows, thresholds):
    output_rows = []
    bucket_bound_rows = []
    for threshold in thresholds:
        threshold_rows = [
            row
            for row in rows
            if as_int(row, "test_support") >= threshold
            and not math.isnan(as_float(row, "log_train_frequency"))
        ]
        log_values = [as_float(row, "log_train_frequency") for row in threshold_rows]
        lower_bound, upper_bound = compute_frequency_bucket_bounds(log_values)
        bucket_bound_rows.append(
            {
                "threshold": threshold,
                "low_upper_bound": lower_bound,
                "mid_upper_bound": upper_bound,
                "n": len(threshold_rows),
            }
        )

        by_bucket = {label: [] for label in FREQUENCY_BUCKET_LABELS}
        for row in threshold_rows:
            bucket_label = frequency_bucket(
                as_float(row, "log_train_frequency"), lower_bound, upper_bound
            )
            by_bucket[bucket_label].append(row)

        for bucket_label in FREQUENCY_BUCKET_LABELS:
            members = by_bucket[bucket_label]
            if not members:
                continue
            row_data = {
                "threshold": threshold,
                "bucket": bucket_label,
                "n": len(members),
                "log_train_frequency_mean": summarize_values(
                    [as_float(row, "log_train_frequency") for row in members]
                )["mean"],
                "train_frequency_mean": summarize_values(
                    [as_int(row, "train_frequency") for row in members]
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
    return output_rows, bucket_bound_rows


def build_summary_lines(rows, correlation_stats, bucket_stats, bucket_bounds, thresholds):
    lines = [
        "Relation Frequency Analysis Summary",
        "",
        f"Merged relations: {len(rows)}",
        (
            "Relations with train_frequency = 0: "
            f"{sum(as_int(row, 'train_frequency') == 0 for row in rows)}"
        ),
        "",
    ]

    for threshold in thresholds:
        kept_rows = [row for row in rows if as_int(row, "test_support") >= threshold]
        bound_row = next(row for row in bucket_bounds if row["threshold"] == threshold)
        lines.append(f"Threshold: test_support >= {threshold}")
        lines.append(f"Relations kept: {len(kept_rows)} / {len(rows)}")
        lines.append(
            "Frequency bucket bounds on log_train_frequency: "
            f"low<={bound_row['low_upper_bound']:.4f}, "
            f"mid<={bound_row['mid_upper_bound']:.4f}, "
            "high>mid"
        )
        for prediction_metric in PREDICTION_METRICS:
            corr_row = next(
                row
                for row in correlation_stats
                if row["threshold"] == threshold
                and row["prediction_metric"] == prediction_metric
            )
            rho = corr_row["spearman_rho"]
            rho_text = "nan" if math.isnan(rho) else f"{rho:.4f}"
            lines.append(
                f"- Spearman(log_train_frequency, {prediction_metric}) = {rho_text} "
                f"(n={corr_row['n']})"
            )

        lines.append("")
        lines.append("Bucket means:")
        threshold_bucket_rows = [
            row for row in bucket_stats if row["threshold"] == threshold
        ]
        for bucket_label in FREQUENCY_BUCKET_LABELS:
            bucket_row = next(
                (row for row in threshold_bucket_rows if row["bucket"] == bucket_label),
                None,
            )
            if bucket_row is None:
                continue
            lines.append(
                f"- {bucket_label}: n={bucket_row['n']}, "
                f"logfreq_mean={bucket_row['log_train_frequency_mean']:.4f}, "
                f"hits_mean={bucket_row['hits_r_mean']:.4f}, "
                f"alpha_mean={bucket_row['alpha_r_mean']:.4f}, "
                f"delta_mean={bucket_row['delta_r_mean']:.4f}"
            )
        lines.append("")

    return lines


def main():
    args = parse_args()
    frequency_rows = load_rows(args.frequency_csv)
    multiplicity_rows = load_rows(args.multiplicity_csv)
    merged_rows = merge_rows(frequency_rows, multiplicity_rows)

    os.makedirs(args.output_dir, exist_ok=True)

    merged_output = os.path.join(
        args.output_dir, "relation_frequency_multiplicity_merged.csv"
    )
    correlation_output = os.path.join(args.output_dir, "correlation_stats.csv")
    bucket_output = os.path.join(args.output_dir, "bucket_stats.csv")
    bucket_bounds_output = os.path.join(args.output_dir, "bucket_bounds.csv")
    summary_output = os.path.join(args.output_dir, "analysis_summary.txt")

    correlation_stats = correlation_rows(merged_rows, args.thresholds)
    bucket_stats, bucket_bounds = bucket_rows(merged_rows, args.thresholds)
    summary_lines = build_summary_lines(
        merged_rows, correlation_stats, bucket_stats, bucket_bounds, args.thresholds
    )

    write_csv(merged_output, merged_rows)
    write_csv(correlation_output, correlation_stats)
    write_csv(bucket_output, bucket_stats)
    write_csv(bucket_bounds_output, bucket_bounds)
    with open(summary_output, "w") as f:
        f.write("\n".join(summary_lines).rstrip() + "\n")

    print(f"Saved merged relation-frequency table to: {merged_output}")
    print(f"Saved relation-frequency correlation stats to: {correlation_output}")
    print(f"Saved relation-frequency bucket stats to: {bucket_output}")
    print(f"Saved relation-frequency bucket bounds to: {bucket_bounds_output}")
    print(f"Saved relation-frequency summary to: {summary_output}")


if __name__ == "__main__":
    main()
