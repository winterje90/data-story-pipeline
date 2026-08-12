---
name: write-story
description: Turn a data findings document (output of /analyze-data) or a user-provided outline into a long-form research article, chart PNG files, and a LinkedIn posting schedule. Use when the user says "write the article", "write this up", "turn the findings into a story", "write a story about [topic]", or after /analyze-data completes. This skill expects either a findings.md from /analyze-data or an outline provided by the user.
---

# Story Writer

Turn a findings document into three deliverables in one pass: a long-form research article (markdown), chart PNG files, and a LinkedIn posting schedule (via the `linkedin-schedule` skill).

## Before You Start

**Announce:** "I'm running `/write-story` — locating the findings document and preparing to write."

Read `output_dir` from `~/.data-story-pipeline.json` (falling back to `./config.json`). Every path
below is relative to it.

## Step 1: Find the Input

**If coming from `/analyze-data`:** Look for the most recently modified `findings.md` under `{output_dir}`. List the files, find the most recent, confirm with the user if more than one exists.

```bash
ls -lt "$OUTPUT_DIR"/*/findings.md 2>/dev/null | head -5
```

**If the user provides an outline:** Use that directly. Ask for the data source, sample size, and time period if not included — these are required for the methodology section.

## Step 2: Create the Output Folder

If a findings doc exists, use its parent folder. Otherwise, create a new one:

```bash
mkdir -p "$OUTPUT_DIR/YYYY-MM-DD-<topic>/charts"
```

Replace `YYYY-MM-DD-<topic>` with today's date and a 2-3 word slug describing the topic.

## Step 3: Write the Long-Form Article

Write the full article to `article.md` in the output folder. Follow this structure exactly:

### Detect Article Mode

Before writing, determine which mode fits the content:

| Mode | Signals | Structure |
|------|---------|-----------|
| **Thesis-driven** | The findings clearly prove or disprove something | Hook → Methodology → Findings → Implications → Caveats |
| **Exploratory** | The findings investigate a question without a definitive answer | Framing question → What we looked at → Data walkthrough → What we explored to explain it → What we can and can't conclude → Caveats |

**Default to exploratory** unless the data unambiguously supports a single thesis. Most real-world data analysis is exploratory.

### Thesis-Driven Structure

**1. Hook (2-4 sentences)**
Lead with the single most surprising or counterintuitive finding. The reader should feel a "wait, that's weird" moment on the first read.

**2. Methodology (2-4 sentences)**
Data source, sample size, time period, what was measured. Short but specific.

**3. Findings (3-5 sections)**
One section per headline finding. Each section: headline stat, explanation, supporting detail, chart reference.

**4. Implications**
What should practitioners do differently? 3-5 specific, actionable points tied to findings.

**5. Caveats**
2-4 sentences on limitations.

### Exploratory Structure

**1. Framing question (2-4 sentences)**
State the question being investigated and why it matters. Don't pretend to know the answer yet.

Good: "Everyone has an opinion on whether AI is reducing headcount at startups. We wanted to see what the data actually shows."
Bad: "AI is fundamentally changing how startups hire. Here's the proof."

**2. What we looked at (2-4 sentences)**
Data source, sample size, filters, time period. Mention any additional analyses upfront (e.g., "we also tested whether macro conditions explain the trends").

**3. Data walkthrough (3-5 sections)**
Each section explores one dimension of the data. Key rules:
- **Show complete tables with every cohort/period.** Never compare only two time points without showing the full trajectory.
- **Present both absolute and normalized metrics** (e.g., units added AND units per dollar). Explain why both matter.
- **Include percentile distributions** (P10, P25, median, P75, P90) not just medians.
- **Add "Notable" callouts** beneath tables to highlight interesting points within the data. It's fine to call out specific cohorts here, as long as the full table is visible above.

**4. What we explored to explain it (1-2 sections)**
Additional analyses performed to test alternative explanations (e.g., macro regression). Frame as "we wanted to check whether X explains this" not "here's our thesis."

**5. What we can and can't conclude**
Honest assessment of confidence level. What the data supports, what it's consistent with but can't prove, and what alternative explanations remain. Don't force a conclusion the data doesn't support.

**6. Caveats and methodology**
Data source details, sample sizes, known limitations, what the data cannot prove.

### Article Voice

- Research-report register: neutral, analytical, let data speak
- Active voice throughout
- Every claim quantified — "62% of companies" not "many companies", "23% faster" not "significantly faster"
- Methodology transparency: cite sample size and source whenever making a claim
- Surface contradictions: at least one finding should challenge something readers assume is true

## Step 4: Generate Charts

For each major finding, write a Python script that generates a PNG chart. Run the script to produce the file.

Save charts to: `{output_dir}/YYYY-MM-DD-<topic>/charts/finding-N.png`

**Choose chart type by finding type:**
- Segment comparison → horizontal or vertical bar chart
- Trend over time → line chart with labeled data points
- Correlation between two variables → scatter plot with trend line
- Feature importance (Random Forest/XGBoost output) → horizontal bar chart, sorted by importance
- Distribution or spread → histogram or box plot

**Chart template (adapt for each finding):**

```python
import os
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Resolve output_dir from config — never hardcode a path
CONFIG = os.path.expanduser('~/.data-story-pipeline.json')
if not os.path.exists(CONFIG):
    CONFIG = 'config.json'
with open(CONFIG) as f:
    OUTPUT_DIR = os.path.expanduser(json.load(f)['output_dir'])

STORY = 'YYYY-MM-DD-topic'   # replace with the actual story folder
charts_dir = os.path.join(OUTPUT_DIR, STORY, 'charts')
os.makedirs(charts_dir, exist_ok=True)

# Style setup — run once
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 12,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
})

fig, ax = plt.subplots(figsize=(12, 6))

# --- Replace below with actual data and chart type ---
categories = ['Cohort A', 'Cohort B', 'Cohort C']
values = [0.62, 0.48, 0.71]

bars = ax.bar(categories, values, color='#2C5F8A', alpha=0.85, width=0.5)

# Labels on bars
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f'{val:.0%}', ha='center', va='bottom', fontweight='bold')

ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax.set_ylim(0, max(values) * 1.2)
# --- End replace ---

ax.set_title('Finding Title Here', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('X Axis Label', fontsize=12)
ax.set_ylabel('Y Axis Label', fontsize=12)

# Source annotation
fig.text(0.12, 0.01, 'Source: [your source]. N=[sample size].',
         fontsize=9, color='#666666')

plt.tight_layout()
plt.savefig(os.path.join(charts_dir, 'finding-1.png'),
            dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print(f"Chart saved to {charts_dir}/finding-1.png")
```

Generate one script per finding, modify the data and chart type, run each one, verify the PNG file was created.

**Chart style rules (non-negotiable):**
- No chartjunk: no 3D effects, no gradients, no unnecessary grid lines, no legend if only one series
- Every chart has: a descriptive title, labeled axes, a source annotation at the bottom
- Consistent primary color (`#2C5F8A` by default; override via `chart_color` in your config file) across all charts in one article
- Minimum 1200px wide (figsize=(12,X) at dpi=150 = ~1800px)
- White background

## Step 5: Invoke `linkedin-schedule`

After the article is written and charts are saved, use the Skill tool to invoke `linkedin-schedule`. It reads the findings document, decomposes it into a multi-post content plan (3-7 posts with different angles, hook patterns, and chart assignments), presents the plan for approval, then writes each post individually via the `linkedin-writer` skill.

Do NOT write LinkedIn posts yourself. `linkedin-schedule` owns the content calendar and post decomposition. `linkedin-writer` owns individual post formatting. Hand off completely.

## Step 6: Save and Confirm

Verify all outputs exist:

```bash
ls "$OUTPUT_DIR/YYYY-MM-DD-<topic>/"
# Expected: article.md, charts/ directory, linkedin-schedule.md, linkedin-posts/ directory
ls "$OUTPUT_DIR/YYYY-MM-DD-<topic>/charts/"
# Expected: finding-1.png, finding-2.png, etc.
ls "$OUTPUT_DIR/YYYY-MM-DD-<topic>/linkedin-posts/"
# Expected: 01-hero-*.md, 02-deep-dive-*.md, etc.
```

Tell the user: "Article, charts, and LinkedIn posting schedule complete. All files saved to `{output_dir}/[folder]/`."

## Publishing the article elsewhere

This skill writes markdown and PNGs to disk. It does not push to Google Docs, Notion, a CMS, or
anywhere else — see "What it can't do" in the repo README. Convert the markdown yourself, or wire
your own export step in after this one.

## Context

This skill is the second step in the data journalism pipeline. The first step is `/analyze-data`, which produces the findings document this skill reads. If you don't have a findings document, run `/analyze-data` first or provide your own outline.
