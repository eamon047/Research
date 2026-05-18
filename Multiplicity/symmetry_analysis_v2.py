import argparse
import math
import os

from symmetry_utils import (
    PREDICTION_METRICS,
    as_float,
    as_int,
    load_rows,
    spearman_correlation,
    summarize_values,
    write_csv,
)


DEFAULT_SYMMETRY_CSV = "results/RotatE_FB15k237/symmetry/relation_symmetry_stats.csv"
DEFAULT_MULTIPLICITY_CSV = (
    "results/RotatE_FB15k237/mapping_type/combined/"
    "relation_metrics_num7_agg7_k10.csv"
)
DEFAULT_OUTPUT_DIR = "results/RotatE_FB15k237/symmetry_v2"
DEFAULT_THRESHOLDS = [0, 5, 10]
MAIN_SYMMETRY_COLUMN = "symmetry_score_excluding_self_loops"
BUCKET_LABELS = ["zero", "weak_nonzero", "high_symmetry"]


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Merge symmetry statistics with relation-level multiplicity results "
            "using the excluding-self-loop symmetry metric."
        )
    )
    parser.add_argument(
        "--symmetry-csv",
        default=DEFAULT_SYMMETRY_CSV,
        help="Relation-level symmetry statistics CSV",
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


def symmetry_bucket(value):
    if value == 0.0:
        return "zero"
    if value <= 0.5:
        return "weak_nonzero"
    return "high_symmetry"


def merge_rows(symmetry_rows, multiplicity_rows):
    multiplicity_by_relation = {row["relation_id"]: row for row in multiplicity_rows}
    merged_rows = []

    for symmetry_row in symmetry_rows:
        relation_id = symmetry_row["relation_id"]
        if relation_id not in multiplicity_by_relation:
            raise KeyError(f"Relation {relation_id} missing from multiplicity table")

        multiplicity_row = multiplicity_by_relation[relation_id]
        if symmetry_row["relation_name"] != multiplicity_row["relation_name"]:
            raise ValueError(
                "Relation name mismatch for relation_id "
                f"{relation_id}: {symmetry_row['relation_name']} vs "
                f"{multiplicity_row['relation_name']}"
            )

        merged_rows.append(
            {
                "relation_id": relation_id,
                "relation_name": symmetry_row["relation_name"],
                "mapping_type": multiplicity_row["mapping_type"],
                "train_support": symmetry_row["train_support"],
                "self_loop_count": symmetry_row["self_loop_count"],
                "non_self_train_support": symmetry_row["non_self_train_support"],
                "symmetric_supported_edge_count": (
                    symmetry_row["symmetric_supported_edge_count"]
                ),
                "symmetric_supported_non_self_edge_count": (
                    symmetry_row["symmetric_supported_non_self_edge_count"]
                ),
                "symmetry_score_raw": symmetry_row["symmetry_score"],
                "symmetry_score": symmetry_row[MAIN_SYMMETRY_COLUMN],
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


def filter_metric_rows(rows, threshold, prediction_metric):
    filtered = []
    for row in rows:
        if as_int(row, "test_support") < threshold:
            continue
        symmetry_value = as_float(row, "symmetry_score")
        prediction_value = as_float(row, prediction_metric)
        if math.isnan(symmetry_value) or math.isnan(prediction_value):
            continue
        filtered.append(row)
    return filtered


def correlation_rows(rows, thresholds):
    output_rows = []
    for threshold in thresholds:
        for prediction_metric in PREDICTION_METRICS:
            filtered = filter_metric_rows(rows, threshold, prediction_metric)
            xs = [as_float(row, "symmetry_score") for row in filtered]
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
    for threshold in thresholds:
        threshold_rows = [
            row
            for row in rows
            if as_int(row, "test_support") >= threshold
            and not math.isnan(as_float(row, "symmetry_score"))
        ]

        by_bucket = {label: [] for label in BUCKET_LABELS}
        for row in threshold_rows:
            by_bucket[symmetry_bucket(as_float(row, "symmetry_score"))].append(row)

        for bucket_label in BUCKET_LABELS:
            members = by_bucket[bucket_label]
            if not members:
                continue
            row_data = {
                "threshold": threshold,
                "bucket": bucket_label,
                "n": len(members),
                "symmetry_score_mean": summarize_values(
                    [as_float(row, "symmetry_score") for row in members]
                )["mean"],
                "symmetry_score_raw_mean": summarize_values(
                    [as_float(row, "symmetry_score_raw") for row in members]
                )["mean"],
                "self_loop_count_mean": summarize_values(
                    [as_int(row, "self_loop_count") for row in members]
                )["mean"],
                "test_support_mean": summarize_values(
                    [as_int(row, "test_support") for row in members]
                )["mean"],
                "train_support_mean": summarize_values(
                    [as_int(row, "train_support") for row in members]
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
    lines = [
        "Symmetry V2 Analysis Summary",
        "",
        "Main symmetry metric: symmetry_score_excluding_self_loops",
        "",
        f"Merged relations: {len(rows)}",
        f"Relations with symmetry_score = 0: "
        f"{sum(as_float(row, 'symmetry_score') == 0.0 for row in rows)}",
        (
            "Relations with high_symmetry (> 0.5): "
            f"{sum(as_float(row, 'symmetry_score') > 0.5 for row in rows)}"
        ),
        (
            "Relations with self_loop_count > 0: "
            f"{sum(as_int(row, 'self_loop_count') > 0 for row in rows)}"
        ),
        "",
    ]

    for threshold in thresholds:
        kept_rows = [row for row in rows if as_int(row, "test_support") >= threshold]
        lines.append(f"Threshold: test_support >= {threshold}")
        lines.append(f"Relations kept: {len(kept_rows)} / {len(rows)}")

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
                f"- Spearman(symmetry_score, {prediction_metric}) = {rho_text} "
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
                f"symmetry_mean={bucket_row['symmetry_score_mean']:.4f}, "
                f"hits_mean={bucket_row['hits_r_mean']:.4f}, "
                f"alpha_mean={bucket_row['alpha_r_mean']:.4f}, "
                f"delta_mean={bucket_row['delta_r_mean']:.4f}"
            )
        lines.append("")

    high_symmetry_rows = sorted(
        [
            row
            for row in rows
            if as_float(row, "symmetry_score") > 0.5
            and as_int(row, "test_support") >= 10
        ],
        key=lambda row: (
            as_float(row, "symmetry_score"),
            as_int(row, "train_support"),
        ),
        reverse=True,
    )
    lines.append("High-symmetry relations (test_support >= 10):")
    for row in high_symmetry_rows[:15]:
        hits = as_float(row, "hits_r")
        alpha = as_float(row, "alpha_r")
        delta = as_float(row, "delta_r")
        lines.append(
            f"- {row['relation_name']}: symmetry={as_float(row, 'symmetry_score'):.4f}, "
            f"raw={as_float(row, 'symmetry_score_raw'):.4f}, "
            f"mapping_type={row['mapping_type']}, "
            f"hits={hits:.4f}, alpha={alpha:.4f}, delta={delta:.4f}, "
            f"self_loop_count={as_int(row, 'self_loop_count')}"
        )

    return lines


def main():
    args = parse_args()
    symmetry_rows = load_rows(args.symmetry_csv)
    multiplicity_rows = load_rows(args.multiplicity_csv)
    merged_rows = merge_rows(symmetry_rows, multiplicity_rows)

    os.makedirs(args.output_dir, exist_ok=True)

    merged_output = os.path.join(
        args.output_dir, "relation_symmetry_multiplicity_merged_v2.csv"
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

    print(f"Saved merged symmetry v2 table to: {merged_output}")
    print(f"Saved symmetry v2 correlation stats to: {correlation_output}")
    print(f"Saved symmetry v2 bucket stats to: {bucket_output}")
    print(f"Saved symmetry v2 summary to: {summary_output}")


if __name__ == "__main__":
    main()
