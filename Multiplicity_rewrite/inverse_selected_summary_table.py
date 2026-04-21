import csv
import os


INPUT_CSV = "results/thesis_selected/inverse_selected_summary.csv"
OUTPUT_SVG = "results/thesis_selected/inverse_selected_summary_table.svg"


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


def draw_cell(svg, x, y, w, h, text, *, fill="white", bold=False, align="left", color="#222222", size=13):
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
        ("Spearman(Hits)", 150, "center"),
        ("Spearman(Alpha)", 155, "center"),
        ("Spearman(Delta)", 155, "center"),
        ("Reading", 220, "left"),
    ]

    draw_cell(svg, left, top, sum(w for _, w, _ in cols), title_h, "Global Trend (threshold = 10)", fill="#eaf2fb", bold=True, size=16)
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
            "No clean global monotonic law",
        ]
        x = left
        for value, (_, width, align) in zip(values, cols):
            draw_cell(svg, x, y, width, row_h, value, align=align, size=14)
            x += width

    return y + row_h


def render_subgroup_section(svg, rows, left, top):
    title_h = 32
    row_h = 34
    cols = [
        ("Model", 90, "left"),
        ("Criterion", 430, "left"),
        ("n", 60, "center"),
        ("Hits@10", 110, "center"),
        ("Alpha", 100, "center"),
        ("Delta", 100, "center"),
    ]

    draw_cell(
        svg,
        left,
        top,
        sum(w for _, w, _ in cols),
        title_h,
        "High-Confidence Inverse-Like Subgroups (threshold = 10)",
        fill="#eef7ea",
        bold=True,
        size=16,
    )
    y = top + title_h
    x = left
    for name, width, align in cols:
        draw_cell(svg, x, y, width, row_h, name, fill="#f5f5f5", bold=True, align=align, size=13)
        x += width

    criterion_map = {
        "mutual_inverse_strength>0.5": "High mutual inverse-like strength (mutual_inverse_strength > 0.5)",
        "inverse_clarity>0.5": "High inverse-like clarity (inverse_clarity > 0.5)",
    }

    for row in rows:
        y += row_h
        values = [
            row["model"],
            criterion_map.get(row["metric_or_group"], row["metric_or_group"]),
            row["n"],
            fmt_float(row["hits_value"]),
            fmt_float(row["alpha_value"]),
            fmt_float(row["delta_value"]),
        ]
        x = left
        for value, (_, width, align) in zip(values, cols):
            draw_cell(svg, x, y, width, row_h, value, align=align, size=12)
            x += width

    return y + row_h


def write_svg(output_path, rows):
    subgroup_rows = [row for row in rows if row["view"] == "selected_bucket"]

    width = 950
    height = 230
    left = 28
    top = 54

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="28" y="30" font-family="Arial" font-size="22" font-weight="700" fill="#111111">Inverse-Like Support Summary</text>',
    ]

    render_subgroup_section(svg, subgroup_rows, left, top)
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
