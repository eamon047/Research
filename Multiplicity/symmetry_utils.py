import csv
import math


PREDICTION_METRICS = ["hits_r", "alpha_r", "delta_r"]


def load_rows(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"No rows found in {path}")
    return rows


def write_csv(path, rows):
    if not rows:
        return
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


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


def summarize_values(values):
    values = sorted(values)
    return {
        "n": len(values),
        "mean": sum(values) / len(values),
        "median": percentile(values, 0.5),
        "p25": percentile(values, 0.25),
        "p75": percentile(values, 0.75),
        "p90": percentile(values, 0.9),
        "min": values[0],
        "max": values[-1],
    }


def average_ranks(values):
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def pearson_correlation(xs, ys):
    if len(xs) != len(ys):
        raise ValueError("Lengths do not match")
    if len(xs) < 2:
        return math.nan

    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = 0.0
    sum_sq_x = 0.0
    sum_sq_y = 0.0
    for x, y in zip(xs, ys):
        dx = x - mean_x
        dy = y - mean_y
        numerator += dx * dy
        sum_sq_x += dx * dx
        sum_sq_y += dy * dy

    denominator = math.sqrt(sum_sq_x * sum_sq_y)
    if denominator == 0.0:
        return math.nan
    return numerator / denominator


def spearman_correlation(xs, ys):
    if len(xs) < 2:
        return math.nan
    return pearson_correlation(average_ranks(xs), average_ranks(ys))


def symmetry_bucket(value):
    if value == 0.0:
        return "zero"
    if value <= 0.1:
        return "(0,0.1]"
    if value <= 0.3:
        return "(0.1,0.3]"
    return "(0.3,1.0]"
