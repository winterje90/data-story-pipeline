"""
01_make_synthetic_source.py — builds the synthetic source dataset for this example.

WHAT IT COMPUTES
    Generates 480 fictional B2B SaaS companies across 4 regions and 4 annual
    cohorts, with a support-desk metric (median ticket resolution hours) and a
    satisfaction score. Stands in for whatever real source you would connect.

PARAMS TO EDIT ON REFRESH
    SEED, N_COMPANIES, REGIONS, COHORTS

VALIDATION VALUES (with SEED=42)
    - writes exactly 480 rows
    - every region appears exactly 120 times
    - no nulls in any column

In a real run this file would instead be `01_<name>.sql` holding the verbatim
warehouse query, or the pandas load + filter for a CSV source.
"""

import csv
import os
import random

SEED = 42
N_COMPANIES = 480
REGIONS = ["Northeast", "Southeast", "Midwest", "West"]
COHORTS = [2022, 2023, 2024, 2025]
OUT = os.path.join(os.path.dirname(__file__), "..", "results", "companies.csv")

# Per-region base resolution hours in the 2022 cohort, and the per-year drift.
# The West starts worst but improves; the Northeast starts best but degrades.
# That tension is what makes this example worth walking through.
REGION_BASE = {"Northeast": 6.0, "Southeast": 9.5, "Midwest": 8.0, "West": 13.0}
REGION_DRIFT = {"Northeast": 1.15, "Southeast": -0.20, "Midwest": 0.05, "West": -1.60}


def main() -> None:
    rng = random.Random(SEED)
    rows = []
    cid = 1000
    per_cell = N_COMPANIES // (len(REGIONS) * len(COHORTS))

    for region in REGIONS:
        for cohort in COHORTS:
            for _ in range(per_cell):
                cid += 1
                years_in = cohort - 2022
                base = REGION_BASE[region] + REGION_DRIFT[region] * years_in
                resolution = max(1.0, rng.gauss(base, 2.2))

                # CSAT falls as resolution time rises, with noise.
                csat = 5.0 - 0.13 * resolution + rng.gauss(0, 0.35)
                csat = round(min(5.0, max(1.0, csat)), 2)

                rows.append(
                    {
                        "company_id": f"C{cid}",
                        "region": region,
                        "cohort_year": cohort,
                        "employees": max(5, int(rng.gauss(180, 90))),
                        "monthly_tickets": max(20, int(rng.gauss(640, 260))),
                        "median_resolution_hours": round(resolution, 2),
                        "csat": csat,
                    }
                )

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()
