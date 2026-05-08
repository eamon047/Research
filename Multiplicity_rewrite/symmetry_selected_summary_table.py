import csv
import os


INPUT_CSV = "results/thesis_selected/symmetry/symmetry_selected_summary.csv"
OUTPUT_SVG = "results/thesis_selected/symmetry/symmetry_selected_summary_table.svg"
OUTPUT_GLOBAL_SVG = "results/thesis_selected/symmetry/symmetry_global_spearman_table.svg"
OUTPUT_BUCKET_SVG = "results/thesis_selected/symmetry/symmetry_bucket_comparison_table.svg"

GLOBAL_TITLE_FILL = "#2A6096"
BUCKET_TITLE_FILL = "#EBF2FA"

PRESENTATION_BUCKET_ROWS = {
    "RotatE": [
        {
            "group": "Zero symmetry",
            "n": "164",
            "hits": "0.5815",
            "alpha": "0.1283",
            "delta": "0.0636",
        },
        {
            "group": "Weak nonzero symmetry (0, 0.5]",
            "n": "6",
            "hits": "0.5047",
            "alpha": "0.2089",
            "delta": "0.1129",
        },
        {
            "group": "High symmetry (> 0.5)",
            "n": "12",
            "hits": "0.5924",
            "alpha": "0.1618",
            "delta": "0.0848",
        },
    ],
    "TransE": [
        {
            "group": "Zero symmetry",
            "n": "164",
            "hits": "0.5605",
            "alpha": "0.3307",
            "delta": "0.1838",
        },
        {
            "group": "Weak nonzero symmetry (0, 0.5]",
            "n": "6",
            "hits": "0.4725",
            "alpha": "0.4436",
            "delta": "0.2736",
        },
        {
            "group": "High symmetry (> 0.5)",
            "n": "12",
            "hits": "0.5742",
            "alpha": "0.3512",
            "delta": "0.2119",
        },
    ],
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
    stroke="#cfcfcf",
):
    svg.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
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
    ]

    draw_cell(
        svg,
        left,
        top,
        sum(w for _, w, _ in cols),
        title_h,
        "Global Spearman Correlation",
        fill=GLOBAL_TITLE_FILL,
        bold=True,
        color="white",
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
        ("Group", 250, "left"),
        ("n", 60, "center"),
        ("Hits@10", 100, "center"),
        ("Alpha", 100, "center"),
        ("Delta", 100, "center"),
    ]

    draw_cell(
        svg,
        left,
        top,
        sum(w for _, w, _ in cols),
        title_h,
        "Bucket Comparison",
        fill=BUCKET_TITLE_FILL,
        bold=True,
        size=16,
    )
    y = top + title_h
    x = left
    for name, width, align in cols:
        draw_cell(svg, x, y, width, row_h, name, fill="#f5f5f5", bold=True, align=align, size=13)
        x += width

    model_order = ["RotatE", "TransE"]
    first_group = True
    total_width = sum(w for _, w, _ in cols)

    for model in model_order:
        model_rows = PRESENTATION_BUCKET_ROWS.get(model, [])
        if not model_rows:
            continue

        if not first_group:
            separator_y = y + row_h
            svg.append(
                f'<rect x="{left}" y="{separator_y}" width="{total_width}" height="8" fill="white"/>'
            )
            y += 8

        for row in model_rows:
            y += row_h
            values = [
                model,
                row["group"],
                row["n"],
                fmt_float(row["hits"]),
                fmt_float(row["alpha"]),
                fmt_float(row["delta"]),
            ]
            x = left
            for value, (_, width, align) in zip(values, cols):
                draw_cell(svg, x, y, width, row_h, value, align=align, size=13)
                x += width

        first_group = False

    return y + row_h


def write_combined_svg(output_path, rows):
    global_rows = [row for row in rows if row["view"] == "global_spearman"]
    bucket_rows = [
        row
        for row in rows
        if row["view"] == "bucket" and row["group_or_metric"] in {"zero", "high_symmetry"}
    ]

    width = 810
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


def write_global_svg(output_path, rows):
    global_rows = [row for row in rows if row["view"] == "global_spearman"]

    width = 660
    height = 170
    left = 28
    top = 24

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]

    render_global_section(svg, global_rows, left, top)
    svg.append("</svg>")

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(svg) + "\n")


def write_bucket_svg(output_path, rows):
    bucket_rows = [
        row
        for row in rows
        if row["view"] == "bucket" and row["group_or_metric"] in {"zero", "high_symmetry"}
    ]

    width = 760
    height = 330
    left = 28
    top = 24

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]

    render_bucket_section(svg, bucket_rows, left, top)
    svg.append("</svg>")

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(svg) + "\n")


def main():
    rows = load_rows(INPUT_CSV)
    write_combined_svg(OUTPUT_SVG, rows)
    write_global_svg(OUTPUT_GLOBAL_SVG, rows)
    write_bucket_svg(OUTPUT_BUCKET_SVG, rows)
    print(f"Saved combined SVG table to: {OUTPUT_SVG}")
    print(f"Saved global SVG table to: {OUTPUT_GLOBAL_SVG}")
    print(f"Saved bucket SVG table to: {OUTPUT_BUCKET_SVG}")


if __name__ == "__main__":
    main()
