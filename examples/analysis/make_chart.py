"""
make_chart.py — renders examples/charts/finding-1.png from computed.json.

Demonstrates the chart rules in the write-story skill: no chartjunk, labeled
axes, source annotation, single primary color family, >=1200px wide, white bg.

USAGE
    python3 make_chart.py
"""

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
COMPUTED = os.path.join(HERE, "computed.json")
OUT_DIR = os.path.join(HERE, "..", "charts")

PRIMARY = "#2C5F8A"
# Muted companions for the non-focal series — the story is Northeast vs West,
# so the other two regions stay visually quiet rather than competing.
MUTED = "#B8C4CE"
ACCENT = "#C1553B"


def main() -> None:
    with open(COMPUTED) as f:
        c = json.load(f)

    matrix = c["resolution_hours_by_region_cohort"]
    cohorts = [str(x) for x in c["cohorts"]]

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.size": 12,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "grid.linestyle": "--",
        }
    )

    fig, ax = plt.subplots(figsize=(12, 6.5))

    styles = {
        "West": dict(color=PRIMARY, lw=2.8, zorder=3),
        "Northeast": dict(color=ACCENT, lw=2.8, zorder=3),
        "Southeast": dict(color=MUTED, lw=1.8, zorder=2),
        "Midwest": dict(color=MUTED, lw=1.8, zorder=2, linestyle="--"),
    }

    # All four regions land within ~1 hour of each other in the final cohort —
    # that convergence IS the story, but it means the right-edge labels collide.
    # Stagger them vertically by hand rather than letting them overlap.
    label_offset = {"Southeast": 16, "Northeast": 2, "West": -13, "Midwest": -27}

    for region, style in styles.items():
        values = [matrix[region][ck] for ck in cohorts]
        ax.plot(cohorts, values, marker="o", markersize=6, **style)
        ax.annotate(
            region,
            xy=(len(cohorts) - 1, values[-1]),
            xytext=(12, label_offset[region]),
            textcoords="offset points",
            va="center",
            fontsize=11,
            fontweight="bold" if region in ("West", "Northeast") else "normal",
            color=style["color"],
        )

    # Label only the endpoints of the two focal series — the whole point is the
    # first-to-last movement, and labeling all 16 points would be noise.
    # Start labels sit above the point; end labels sit left of it, clear of the
    # region names on the right.
    for region in ("West", "Northeast"):
        values = [matrix[region][ck] for ck in cohorts]
        last = len(cohorts) - 1
        ax.annotate(
            f"{values[0]:.1f}h",
            xy=(0, values[0]),
            xytext=(0, 12),
            textcoords="offset points",
            ha="center",
            fontsize=10,
            fontweight="bold",
            color=styles[region]["color"],
        )
        ax.annotate(
            f"{values[last]:.1f}h",
            xy=(last, values[last]),
            xytext=(-10, 11 if region == "Northeast" else -16),
            textcoords="offset points",
            ha="right",
            fontsize=10,
            fontweight="bold",
            color=styles[region]["color"],
        )

    ax.set_title(
        "The fastest region is the only one getting slower",
        fontsize=16,
        fontweight="bold",
        pad=15,
        loc="left",
    )
    ax.set_xlabel("Cohort year", fontsize=12)
    ax.set_ylabel("Median ticket resolution (hours)", fontsize=12)
    ax.set_ylim(0, 14)
    ax.set_xlim(-0.15, len(cohorts) - 0.62)

    fig.text(
        0.125,
        0.015,
        "Source: synthetic example data (data-story-pipeline). N=480 fictional companies.",
        fontsize=9,
        color="#666666",
    )

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "finding-1.png")
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Chart saved to {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
