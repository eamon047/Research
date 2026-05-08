import csv
import os


INPUTS = {
    "RotatE": "results/RotatE_FB15k237/inverse_v2/relation_inverse_multiplicity_merged_v2.csv",
    "TransE": "results/TransE_FB15k237/inverse_v2/relation_inverse_multiplicity_merged_v2.csv",
}
OUTPUT_CSV = "results/thesis_selected/inverse/inverse_selected_relation_baseline_summary.csv"
OUTPUT_SVG = "results/thesis_selected/inverse/inverse_selected_relation_baseline_table.svg"

THRESHOLD = 10
GLOBAL_BASELINES = {
    "RotatE": {"hits": 0.5797, "alpha": 0.163, "delta": 0.064},
    "TransE": {"hits": 0.5585, "alpha": 0.385, "delta": 0.145},
}


def load_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def as_float(row, key):
    value = row[key]
    if value == "" or value.lower() == "nan":
        return None
    return float(value)


def summarize(rows):
    if not rows:
        raise ValueError("Cannot summarize an empty row set")

    hits_values = [as_float(row, "hits_r") for row in rows]
    alpha_values = [as_float(row, "alpha_r") for row in rows]
    delta_values = [as_float(row, "delta_r") for row in rows]

    hits_values = [value for value in hits_values if value is not None]
    alpha_values = [value for value in alpha_values if value is not None]
    delta_values = [value for value in delta_values if value is not None]

    return {
        "n_relations": len(rows),
        "test_triples": sum(int(row["test_support"]) for row in rows),
        "eligible_support": sum(int(row["eligible_support"]) for row in rows),
        "hits_mean": sum(hits_values) / len(hits_values),
        "alpha_mean": sum(alpha_values) / len(alpha_values),
        "delta_mean": sum(delta_values) / len(delta_values),
    }


def build_summary_rows():
    output_rows = []
    groups = [
        (
            "All relations (global baseline)",
            "all_relations",
            lambda row: True,
            "paper_global_reference",
        ),
        (
            "High mutual inverse-like strength (> 0.5)",
            "mutual_inverse_strength_gt_0.5",
            lambda row: float(row["mutual_inverse_strength"]) > 0.5,
            "high_strength_subgroup",
        ),
        (
            "High inverse-like clarity (> 0.5)",
            "inverse_clarity_gt_0.5",
            lambda row: float(row["inverse_clarity"]) > 0.5,
            "very_clear_subgroup",
        ),
    ]

    for model, path in INPUTS.items():
        rows = [
            row
            for row in load_rows(path)
            if int(row["test_support"]) >= THRESHOLD
        ]
        for label, key, predicate, reading in groups:
            if key == "all_relations":
                baseline = GLOBAL_BASELINES[model]
                summary = summarize(rows)
                output_rows.append(
                    {
                        "model": model,
                        "threshold": THRESHOLD,
                        "group": label,
                        "group_key": key,
                        "n_relations": summary["n_relations"],
                        "test_triples": summary["test_triples"],
                        "eligible_support": summary["eligible_support"],
                        "hits_mean": f"{baseline['hits']:.4f}",
                        "alpha_mean": f"{baseline['alpha']:.4f}",
                        "delta_mean": f"{baseline['delta']:.4f}",
                        "reading": reading,
                    }
                )
                continue

            group_rows = [row for row in rows if predicate(row)]
            summary = summarize(group_rows)
            output_rows.append(
                {
                    "model": model,
                    "threshold": THRESHOLD,
                    "group": label,
                    "group_key": key,
                    "n_relations": summary["n_relations"],
                    "test_triples": summary["test_triples"],
                    "eligible_support": summary["eligible_support"],
                    "hits_mean": f"{summary['hits_mean']:.4f}",
                    "alpha_mean": f"{summary['alpha_mean']:.4f}",
                    "delta_mean": f"{summary['delta_mean']:.4f}",
                    "reading": reading,
                }
            )

    return output_rows


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def xml_escape(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def draw_cell(
    svg,
    x,
    y,
    w,
    h,
    text,
    *,
    fill="white",
    bold=False,
    align="left",
    color="#222222",
    size=13,
):
    svg.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
        'stroke="#cfcfcf" stroke-width="1"/>'
    )
    if align == "left":
        text_x = x + 10
        anchor = "start"
    elif align == "center":
        text_x = x + w / 2
        anchor = "middle"
    else:
        text_x = x + w - 10
        anchor = "end"
    weight = "700" if bold else "400"
    svg.append(
        f'<text x="{text_x}" y="{y + h / 2 + 5}" text-anchor="{anchor}" '
        f'font-family="Arial" font-size="{size}" font-weight="{weight}" '
        f'fill="{color}">{xml_escape(text)}</text>'
    )


def render_table(svg, rows, left, top):
    title_h = 34
    row_h = 36
    spacer_h = 12
    cols = [
        ("Model", 90, "left"),
        ("Relations", 335, "left"),
        ("n_rel", 70, "center"),
        ("test triples", 95, "center"),
        ("Hits@10", 95, "center"),
        ("Alpha", 85, "center"),
        ("Delta", 85, "center"),
    ]
    total_w = sum(width for _, width, _ in cols)

    draw_cell(
        svg,
        left,
        top,
        total_w,
        title_h,
        "Inverse-Like Support and Predictive Stability",
        fill="#DDEAF6",
        bold=True,
        size=16,
    )

    y = top + title_h
    x = left
    for name, width, align in cols:
        draw_cell(
            svg,
            x,
            y,
            width,
            row_h,
            name,
            fill="#f5f5f5",
            bold=True,
            align=align,
            size=13,
        )
        x += width

    model_order = ["RotatE", "TransE"]
    group_order = [
        "All relations (global baseline)",
        "High mutual inverse-like strength (> 0.5)",
        "High inverse-like clarity (> 0.5)",
    ]
    by_key = {(row["model"], row["group"]): row for row in rows}
    first_model = True
    for model in model_order:
        if not first_model:
            spacer_top = y + row_h
            draw_cell(
                svg,
                left,
                spacer_top,
                total_w,
                spacer_h,
                "",
                fill="#ffffff",
                size=1,
            )
            y = spacer_top + spacer_h - row_h

        for group in group_order:
            row = by_key[(model, group)]
            y += row_h
            is_reference = group == "All relations (global baseline)"
            fill = "#f3f3f3" if is_reference else "#ffffff"

            values = [
                row["model"],
                row["group"],
                row["n_relations"],
                row["test_triples"],
                row["hits_mean"],
                row["alpha_mean"],
                row["delta_mean"],
            ]
            x = left
            for value, (_, width, align) in zip(values, cols):
                draw_cell(
                    svg,
                    x,
                    y,
                    width,
                    row_h,
                    value,
                    fill=fill,
                    bold=False,
                    align=align,
                    size=12,
                )
                x += width

        first_model = False

    return y + row_h, total_w


def write_svg(path, rows):
    width = 875
    height = 318
    left = 10
    top = 10
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]

    render_table(svg, rows, left, top)
    svg.append("</svg>")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(svg) + "\n")


def main():
    rows = build_summary_rows()
    write_csv(OUTPUT_CSV, rows)
    write_svg(OUTPUT_SVG, rows)
    print(f"Saved CSV to: {OUTPUT_CSV}")
    print(f"Saved SVG table to: {OUTPUT_SVG}")


if __name__ == "__main__":
    main()
