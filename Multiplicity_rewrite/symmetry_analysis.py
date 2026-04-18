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
    symmetry_bucket,
    write_csv,
)


DEFAULT_SYMMETRY_CSV = "results/RotatE_FB15k237/symmetry/relation_symmetry_stats.csv"
DEFAULT_MULTIPLICITY_CSV = (
    "results/RotatE_FB15k237/mapping_type/combined/"
    "relation_metrics_num7_agg7_k10.csv"
)
DEFAULT_OUTPUT_DIR = "results/RotatE_FB15k237/symmetry"
DEFAULT_THRESHOLDS = [0, 5, 10]


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Merge symmetry statistics with relation-level multiplicity results and "
            "compute correlation and bucket summaries."
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
                "symmetry_score": symmetry_row["symmetry_score"],
                "symmetry_score_excluding_self_loops": (
                    symmetry_row["symmetry_score_excluding_self_loops"]
                ),
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

        bucket_map = {}
        for row in threshold_rows:
            label = symmetry_bucket(as_float(row, "symmetry_score"))
            bucket_map.setdefault(label, []).append(row)

        for bucket_label in ["zero", "(0,0.1]", "(0.1,0.3]", "(0.3,1.0]"]:
            members = bucket_map.get(bucket_label, [])
            if not members:
                continue

            row_data = {
                "threshold": threshold,
                "bucket": bucket_label,
                "n": len(members),
                "symmetry_score_mean": summarize_values(
                    [as_float(row, "symmetry_score") for row in members]
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
        "Symmetry Analysis Summary",
        "",
        f"Merged relations: {len(rows)}",
        f"Relations with symmetry_score = 0: "
        f"{sum(as_float(row, 'symmetry_score') == 0.0 for row in rows)}",
        (
            "Relations with symmetry_score > 0.5: "
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
        for bucket_label in ["zero", "(0,0.1]", "(0.1,0.3]", "(0.3,1.0]"]:
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

    top_high = sorted(
        rows,
        key=lambda row: (
            as_float(row, "symmetry_score"),
            as_int(row, "symmetric_supported_edge_count"),
            as_int(row, "train_support"),
        ),
        reverse=True,
    )[:10]

    lines.append("Top symmetry relations after merge:")
    for row in top_high:
        lines.append(
            f"- {row['relation_name']}: symmetry={as_float(row, 'symmetry_score'):.4f}, "
            f"mapping_type={row['mapping_type']}, "
            f"hits={as_float(row, 'hits_r'):.4f}, "
            f"alpha={as_float(row, 'alpha_r'):.4f}, "
            f"delta={as_float(row, 'delta_r'):.4f}"
        )

    return lines


def main():
    args = parse_args()
    symmetry_rows = load_rows(args.symmetry_csv)
    multiplicity_rows = load_rows(args.multiplicity_csv)
    merged_rows = merge_rows(symmetry_rows, multiplicity_rows)

    os.makedirs(args.output_dir, exist_ok=True)

    merged_output = os.path.join(
        args.output_dir, "relation_symmetry_multiplicity_merged.csv"
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

    print(f"Saved merged symmetry table to: {merged_output}")
    print(f"Saved symmetry correlation stats to: {correlation_output}")
    print(f"Saved symmetry bucket stats to: {bucket_output}")
    print(f"Saved symmetry summary to: {summary_output}")


if __name__ == "__main__":
    main()
