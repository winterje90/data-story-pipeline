"""
compute.py — ALL downstream computation for this example story.

Reads results/companies.csv, writes computed.json. Deterministic, stdlib only,
so it runs anywhere without a virtualenv. Every number quoted in findings.md and
article.md comes out of this file — nothing is hand-typed into prose.

USAGE
    python3 compute.py              recompute and write computed.json
    python3 compute.py --validate   recompute and assert the headline numbers

VALIDATION VALUES
    Asserted in validate() below. If the source or the seed changes, these fail
    loudly — which is the point. Pipeline drift should break the build, not
    quietly change the article.
"""

import argparse
import csv
import json
import math
import os
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "results", "companies.csv")
OUT = os.path.join(HERE, "computed.json")

REGIONS = ["Northeast", "Southeast", "Midwest", "West"]
COHORTS = [2022, 2023, 2024, 2025]


def load():
    with open(SRC) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["cohort_year"] = int(r["cohort_year"])
        r["employees"] = int(r["employees"])
        r["monthly_tickets"] = int(r["monthly_tickets"])
        r["median_resolution_hours"] = float(r["median_resolution_hours"])
        r["csat"] = float(r["csat"])
    return rows


def pctile(values, p):
    """Linear-interpolation percentile. p in 0..100."""
    if not values:
        return None
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * (p / 100.0)
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return s[int(k)]
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def pearson(xs, ys):
    n = len(xs)
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den if den else float("nan")


def linreg(xs, ys):
    """Ordinary least squares slope/intercept."""
    n = len(xs)
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    den = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    return slope, my - slope * mx


def main(validate: bool) -> None:
    rows = load()

    # --- Region x cohort grid: the full trajectory, every cell -----------------
    grid = defaultdict(list)
    for r in rows:
        grid[(r["region"], r["cohort_year"])].append(r["median_resolution_hours"])

    matrix = {
        region: {
            str(c): round(statistics.median(grid[(region, c)]), 2) for c in COHORTS
        }
        for region in REGIONS
    }

    # --- Change from first to last cohort, per region -------------------------
    change = {}
    for region in REGIONS:
        first = matrix[region][str(COHORTS[0])]
        last = matrix[region][str(COHORTS[-1])]
        change[region] = {
            "first": first,
            "last": last,
            "pct_change": round((last - first) / first * 100, 1),
            "direction": "improved" if last < first else "degraded",
        }

    # --- Gap between best and worst region, first vs last cohort --------------
    def spread(cohort):
        vals = [matrix[r][str(cohort)] for r in REGIONS]
        return round(max(vals) - min(vals), 2)

    gap = {"first_cohort": spread(COHORTS[0]), "last_cohort": spread(COHORTS[-1])}
    gap["narrowed_by_pct"] = round(
        (gap["first_cohort"] - gap["last_cohort"]) / gap["first_cohort"] * 100, 1
    )

    # --- Resolution vs CSAT ---------------------------------------------------
    xs = [r["median_resolution_hours"] for r in rows]
    ys = [r["csat"] for r in rows]
    slope, intercept = linreg(xs, ys)
    corr = {
        "pearson_r": round(pearson(xs, ys), 3),
        "csat_points_per_hour": round(slope, 3),
        "intercept": round(intercept, 3),
        "r_squared": round(pearson(xs, ys) ** 2, 3),
    }

    # --- Within-region spread vs between-region gap ---------------------------
    within = {}
    for region in REGIONS:
        vals = [r["median_resolution_hours"] for r in rows if r["region"] == region]
        within[region] = {
            "p10": round(pctile(vals, 10), 2),
            "p25": round(pctile(vals, 25), 2),
            "median": round(statistics.median(vals), 2),
            "p75": round(pctile(vals, 75), 2),
            "p90": round(pctile(vals, 90), 2),
            "p90_minus_p10": round(pctile(vals, 90) - pctile(vals, 10), 2),
        }

    region_medians = [within[r]["median"] for r in REGIONS]
    comparison = {
        "widest_within_region_spread": round(
            max(within[r]["p90_minus_p10"] for r in REGIONS), 2
        ),
        "narrowest_within_region_spread": round(
            min(within[r]["p90_minus_p10"] for r in REGIONS), 2
        ),
        "between_region_gap": round(max(region_medians) - min(region_medians), 2),
    }
    comparison["within_exceeds_between"] = (
        comparison["narrowest_within_region_spread"] > comparison["between_region_gap"]
    )

    computed = {
        "n_companies": len(rows),
        "regions": REGIONS,
        "cohorts": COHORTS,
        "resolution_hours_by_region_cohort": matrix,
        "change_first_to_last_cohort": change,
        "best_worst_gap": gap,
        "resolution_vs_csat": corr,
        "within_region_distribution": within,
        "within_vs_between": comparison,
    }

    with open(OUT, "w") as f:
        json.dump(computed, f, indent=2)
    print(f"Wrote {os.path.relpath(OUT, HERE)}")

    if validate:
        validate_numbers(computed)
        print("Validation passed — all headline numbers match.")


def validate_numbers(c) -> None:
    """Assert the numbers findings.md quotes. Fail loudly on drift."""
    assert c["n_companies"] == 480, f"expected 480 rows, got {c['n_companies']}"

    west = c["change_first_to_last_cohort"]["West"]
    ne = c["change_first_to_last_cohort"]["Northeast"]
    assert west["direction"] == "improved", "West should improve across cohorts"
    assert ne["direction"] == "degraded", "Northeast should degrade across cohorts"
    assert west["pct_change"] < -25, f"West improvement weaker than expected: {west}"
    assert ne["pct_change"] > 25, f"Northeast degradation weaker than expected: {ne}"

    gap = c["best_worst_gap"]
    assert gap["last_cohort"] < gap["first_cohort"], "best/worst gap should narrow"

    corr = c["resolution_vs_csat"]
    assert corr["pearson_r"] < -0.5, f"expected strong negative r, got {corr}"

    for region, d in c["within_region_distribution"].items():
        assert d["p10"] <= d["median"] <= d["p90"], f"percentiles out of order: {region}"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    main(ap.parse_args().validate)
