import csv
import os


INPUT_CSV = "results/thesis_selected/symmetry/symmetry_selected_summary.csv"
OUTPUT_SVG = "results/thesis_selected/symmetry/symmetry_selected_summary_table.svg"
PAPER_BASELINES = {
    "RotatE": {"hits": 0.520, "alpha": 0.163, "delta": 0.064},
    "TransE": {"hits": 0.455, "alpha": 0.385, "delta": 0.145},
}


def load_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def xml_escape(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def fmt_float(value):
    return f"{float(value):.4f}"


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
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#cfcfcf" stroke-width="1"/>'
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
        f'font-family="Arial" font-size="{size}" font-weight="{weight}" fill="{color}">{xml_escape(text)}</text>'
    )


def render_global_section(svg, rows, left, top):
    title_h = 32
    row_h = 34
    cols = [
        ("Model", 90, "left"),
        ("n", 60, "center"),
        ("Spearman(Hits)", 145, "center"),
        ("Spearman(Alpha)", 150, "center"),
        ("Spearman(Delta)", 150, "center"),
        ("Reading", 295, "left"),
    ]

    draw_cell(
        svg,
        left,
        top,
        sum(w for _, w, _ in cols),
        title_h,
        "Global Trend (threshold = 10)",
        fill="#eaf2fb",
        bold=True,
        size=16,
    )
    y = top + title_h
    x = left
    for name, width, align in cols:
        draw_cell(svg, x, y, width, row_h, name, fill="#f5f5f5", bold=True, align=align, size=14)
        x += width

    for row in rows:
        y += row_h
        values = [
            row["model"],
            row["n"],
            fmt_float(row["hits_value"]),
            fmt_float(row["alpha_value"]),
            fmt_float(row["delta_value"]),
            "Near-zero global association",
        ]
        x = left
        for value, (_, width, align) in zip(values, cols):
            draw_cell(svg, x, y, width, row_h, value, align=align, size=14)
            x += width

    return y + row_h


def render_bucket_section(svg, rows, left, top):
    title_h = 32
    row_h = 34
    cols = [
        ("Model", 90, "left"),
        ("Group", 180, "left"),
        ("n", 60, "center"),
        ("Hits@10", 100, "center"),
        ("Alpha", 100, "center"),
        ("Delta", 100, "center"),
        ("Reading", 260, "left"),
    ]

    draw_cell(
        svg,
        left,
        top,
        sum(w for _, w, _ in cols),
        title_h,
        "Bucket Comparison (threshold = 10)",
        fill="#f9efe2",
        bold=True,
        size=16,
    )
    y = top + title_h
    x = left
    for name, width, align in cols:
        draw_cell(svg, x, y, width, row_h, name, fill="#f5f5f5", bold=True, align=align, size=13)
        x += width

    group_map = {
        "zero": "Zero symmetry",
        "high_symmetry": "High symmetry (> 0.5)",
    }
    reading_map = {
        "main_reference_group": "Reference group",
        "no_clean_benefit": "Not cleaner than zero-symmetry",
    }
    grouped_rows = {}
    for row in rows:
        grouped_rows.setdefault(row["model"], []).append(row)

    model_order = ["RotatE", "TransE"]
    first_group = True
    total_width = sum(w for _, w, _ in cols)

    for model in model_order:
        model_rows = grouped_rows.get(model, [])
        if not model_rows:
            continue

        if not first_group:
            svg.append(
                f'<line x1="{left}" y1="{y + row_h}" x2="{left + total_width}" y2="{y + row_h}" '
                'stroke="#9e9e9e" stroke-width="2.2"/>'
            )

        for row in model_rows:
            y += row_h
            values = [
                row["model"],
                group_map.get(row["group_or_metric"], row["group_or_metric"]),
                row["n"],
                fmt_float(row["hits_value"]),
                fmt_float(row["alpha_value"]),
                fmt_float(row["delta_value"]),
                reading_map.get(row["reading"], row["reading"]),
            ]
            x = left
            for value, (_, width, align) in zip(values, cols):
                draw_cell(svg, x, y, width, row_h, value, align=align, size=13)
                x += width

        baseline = PAPER_BASELINES.get(model)
        if baseline:
            y += row_h
            values = [
                model,
                "Overall baseline",
                "-",
                fmt_float(baseline["hits"]),
                fmt_float(baseline["alpha"]),
                fmt_float(baseline["delta"]),
                "Overall reference row",
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
                    align=align,
                    size=12,
                    fill="#f3f3f3",
                    color="#444444",
                )
                x += width

        first_group = False

    return y + row_h


def write_svg(output_path, rows):
    global_rows = [row for row in rows if row["view"] == "global_spearman"]
    bucket_rows = [
        row
        for row in rows
        if row["view"] == "bucket" and row["group_or_metric"] in {"zero", "high_symmetry"}
    ]

    width = 1020
    height = 500
    left = 28
    top = 54

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="28" y="30" font-family="Arial" font-size="22" font-weight="700" fill="#111111">Symmetry Summary</text>',
    ]

    bottom_y = render_global_section(svg, global_rows, left, top)
    render_bucket_section(svg, bucket_rows, left, bottom_y + 24)
    svg.append("</svg>")

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(svg) + "\n")


def main():
    rows = load_rows(INPUT_CSV)
    write_svg(OUTPUT_SVG, rows)
    print(f"Saved SVG table to: {OUTPUT_SVG}")


if __name__ == "__main__":
    main()
