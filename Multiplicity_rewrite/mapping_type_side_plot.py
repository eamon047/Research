import argparse
import csv
import math
import os


DEFAULT_THRESHOLDS = [5, 10]
DEFAULT_METRICS = ["hits_r", "alpha_r", "delta_r"]
MAPPING_TYPE_ORDER = ["1-1", "1-N", "M-1", "M-N"]
SIDES = ["head", "tail"]
METRIC_LABELS = {
    "hits_r": "Hits@10",
    "alpha_r": "Alpha",
    "delta_r": "Delta",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create boxplot SVGs for mapping-type by-side analysis."
    )
    parser.add_argument(
        "--input-csv",
        default=(
            "results/RotatE_FB15k237/mapping_type/by_side/"
            "relation_metrics_num7_agg7_k10.csv"
        ),
        help="Path to side-aware relation-level CSV",
    )
    parser.add_argument(
        "--output-svg",
        default="results/RotatE_FB15k237/mapping_type/by_side/boxplots.svg",
        help="Output SVG path",
    )
    parser.add_argument(
        "--thresholds",
        nargs="*",
        type=int,
        default=DEFAULT_THRESHOLDS,
        help="Minimum test_support thresholds to visualize",
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


def boxplot_stats(values):
    values = sorted(values)
    return {
        "min": values[0],
        "q1": percentile(values, 0.25),
        "median": percentile(values, 0.5),
        "q3": percentile(values, 0.75),
        "max": values[-1],
        "n": len(values),
    }


def xml_escape(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def y_to_svg(value, top, height):
    return top + (1.0 - value) * height


def collect_values(rows, threshold, side, metric):
    kept_rows = [
        row
        for row in rows
        if as_int(row, "test_support") >= threshold and row["side"] == side
    ]
    collected = {}
    for mapping_type in MAPPING_TYPE_ORDER:
        values = [
            as_float(row, metric)
            for row in kept_rows
            if row["mapping_type"] == mapping_type and not math.isnan(as_float(row, metric))
        ]
        collected[mapping_type] = values
    return kept_rows, collected


def draw_panel(
    svg_parts,
    panel_left,
    panel_top,
    panel_width,
    panel_height,
    threshold,
    side,
    metric,
    values_by_type,
):
    title_y = panel_top + 22
    chart_top = panel_top + 40
    chart_height = panel_height - 88
    chart_left = panel_left + 50
    chart_width = panel_width - 70
    chart_bottom = chart_top + chart_height

    svg_parts.append(
        f'<rect x="{panel_left}" y="{panel_top}" width="{panel_width}" height="{panel_height}" '
        'fill="white" stroke="#d9d9d9" stroke-width="1"/>'
    )
    svg_parts.append(
        f'<text x="{panel_left + 10}" y="{title_y}" font-size="13" font-family="Arial" fill="#111111">'
        f'{xml_escape(f"{METRIC_LABELS[metric]} | {side} | >= {threshold}")}</text>'
    )

    for tick in [0.0, 0.25, 0.5, 0.75, 1.0]:
        y = y_to_svg(tick, chart_top, chart_height)
        svg_parts.append(
            f'<line x1="{chart_left}" y1="{y}" x2="{chart_left + chart_width}" y2="{y}" '
            'stroke="#ededed" stroke-width="1"/>'
        )
        svg_parts.append(
            f'<text x="{chart_left - 8}" y="{y + 4}" text-anchor="end" font-size="10" '
            'font-family="Arial" fill="#666666">'
            f'{tick:.2f}</text>'
        )

    svg_parts.append(
        f'<line x1="{chart_left}" y1="{chart_bottom}" x2="{chart_left + chart_width}" y2="{chart_bottom}" '
        'stroke="#999999" stroke-width="1.1"/>'
    )

    slot_width = chart_width / len(MAPPING_TYPE_ORDER)
    box_width = 28
    colors = {
        "1-1": "#4e79a7",
        "1-N": "#f28e2b",
        "M-1": "#59a14f",
        "M-N": "#e15759",
    }

    for index, mapping_type in enumerate(MAPPING_TYPE_ORDER):
        values = values_by_type.get(mapping_type, [])
        center_x = chart_left + slot_width * (index + 0.5)
        label_y = chart_bottom + 18
        count_y = chart_bottom + 32

        svg_parts.append(
            f'<text x="{center_x}" y="{label_y}" text-anchor="middle" font-size="10" '
            'font-family="Arial" fill="#444444">'
            f"{xml_escape(mapping_type)}</text>"
        )

        if not values:
            svg_parts.append(
                f'<text x="{center_x}" y="{count_y}" text-anchor="middle" font-size="9" '
                'font-family="Arial" fill="#999999">n=0</text>'
            )
            continue

        stats = boxplot_stats(values)
        q1_y = y_to_svg(stats["q1"], chart_top, chart_height)
        median_y = y_to_svg(stats["median"], chart_top, chart_height)
        q3_y = y_to_svg(stats["q3"], chart_top, chart_height)
        min_y = y_to_svg(stats["min"], chart_top, chart_height)
        max_y = y_to_svg(stats["max"], chart_top, chart_height)
        color = colors[mapping_type]

        svg_parts.append(
            f'<line x1="{center_x}" y1="{min_y}" x2="{center_x}" y2="{max_y}" '
            f'stroke="{color}" stroke-width="1.3"/>'
        )
        svg_parts.append(
            f'<line x1="{center_x - 8}" y1="{min_y}" x2="{center_x + 8}" y2="{min_y}" '
            f'stroke="{color}" stroke-width="1.3"/>'
        )
        svg_parts.append(
            f'<line x1="{center_x - 8}" y1="{max_y}" x2="{center_x + 8}" y2="{max_y}" '
            f'stroke="{color}" stroke-width="1.3"/>'
        )
        svg_parts.append(
            f'<rect x="{center_x - box_width / 2}" y="{q3_y}" width="{box_width}" height="{q1_y - q3_y}" '
            f'fill="{color}" fill-opacity="0.22" stroke="{color}" stroke-width="1.3"/>'
        )
        svg_parts.append(
            f'<line x1="{center_x - box_width / 2}" y1="{median_y}" x2="{center_x + box_width / 2}" '
            f'y2="{median_y}" stroke="{color}" stroke-width="1.8"/>'
        )
        svg_parts.append(
            f'<text x="{center_x}" y="{count_y}" text-anchor="middle" font-size="9" '
            'font-family="Arial" fill="#777777">'
            f'n={stats["n"]}</text>'
        )


def write_svg(path, rows, thresholds, metrics):
    panel_width = 280
    panel_height = 230
    left_margin = 24
    top_margin = 44
    gap_x = 16
    gap_y = 18
    cols = len(metrics)
    rows_count = len(thresholds) * len(SIDES)
    width = left_margin * 2 + cols * panel_width + (cols - 1) * gap_x
    height = top_margin * 2 + rows_count * panel_height + (rows_count - 1) * gap_y + 20

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fafafa"/>',
        '<text x="24" y="26" font-size="20" font-family="Arial" fill="#111111">'
        'Mapping-Type By-Side Analysis</text>',
    ]

    panel_row = 0
    for threshold in thresholds:
        for side in SIDES:
            for col_index, metric in enumerate(metrics):
                panel_left = left_margin + col_index * (panel_width + gap_x)
                panel_top = top_margin + panel_row * (panel_height + gap_y)
                _kept_rows, values_by_type = collect_values(rows, threshold, side, metric)
                draw_panel(
                    svg_parts,
                    panel_left,
                    panel_top,
                    panel_width,
                    panel_height,
                    threshold,
                    side,
                    metric,
                    values_by_type,
                )
            panel_row += 1

    svg_parts.append("</svg>")

    output_dir = os.path.dirname(path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(svg_parts) + "\n")


def main():
    args = parse_args()
    rows = load_rows(args.input_csv)
    write_svg(args.output_svg, rows, args.thresholds, DEFAULT_METRICS)
    print(f"Saved SVG to: {args.output_svg}")


if __name__ == "__main__":
    main()
