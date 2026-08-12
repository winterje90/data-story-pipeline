---
name: analyze-data
description: Analyze a dataset from a CSV file, a database, or any connected data source using data science techniques, and surface publishable findings. Use when the user wants to explore data, test a hypothesis, find narrative angles in a dataset, or says "analyze this data / table / dataset". Also triggers on thesis-driven prompts like "are Series A companies over-hiring?" or brief-driven prompts like "I want to write about AI hiring trends — find me the data."
---

# Data Analyst

Turn a raw dataset into a structured findings document: quantified headline findings, narrative angles, and chart recommendations — ready to hand off to `/write-story`.

## Before You Start

**Announce:** "I'm running `/analyze-data` — detecting your starting mode and beginning analysis."

Read the config file at `~/.data-story-pipeline.json` (falling back to `./config.json` in the
current directory). Copy `config.example.json` from the repo to that path if it doesn't exist yet.
You need `output_dir` before you can save anything. If no config is found, ask the user where
output should go and offer to create it.

## Step 0: Confirm Scope and Filters

Before running any queries, confirm the scope of the analysis with the user. Ask:
- **Population:** the whole dataset, or a subset? (e.g., US companies only)
- **Segment:** any category filter? (e.g., B2B SaaS only)
- **Cohort:** any stage/tier/band filter? (e.g., Series A only)
- **Time period:** any preference on date range?

If the user's prompt already specifies these (e.g., "US B2B SaaS Series A companies"), confirm and move on. Don't re-ask what's already stated. But if the prompt is vague (e.g., "look at hiring trends"), ask before querying.

## Step 1: Detect Starting Mode

Read the user's prompt and identify which mode applies:

| Mode | Signals | What to do |
|------|---------|-----------|
| **Data-first** | "Analyze [table/dataset]", "what does this data show?" | Explore the dataset, find what's interesting |
| **Thesis-first** | "Are X companies doing Y?", "prove/disprove that..." | Query specifically to test the hypothesis |
| **Brief-first** | "I want to write about X", "find me data on Y" | Identify which tables/fields are relevant first, then explore |

## Step 2: Connect to the Data Source

This skill is source-agnostic. Establish where the data lives before writing a single query.

### CSV / local files (the default path — no external accounts needed)

```python
import pandas as pd
df = pd.read_csv('path/to/file.csv')
print(df.shape)
print(df.dtypes)
print(df.head())
```

Profile the file before analyzing it: row count, column types, null rates, and cardinality of each
categorical column. You cannot pick techniques for a dataset you haven't looked at.

```python
print(df.isna().mean().sort_values(ascending=False))   # null rate per column
print(df.select_dtypes('object').nunique())            # cardinality of categoricals
```

### A database or warehouse (optional)

If the user has a warehouse connected — Postgres, BigQuery, Snowflake, DuckDB, or anything reachable
through an MCP server or a Python driver — query it directly instead. Use whatever connection the
user already has configured; do not assume a specific vendor.

**If the source has a data dictionary**, read it before writing any queries. Set `data_dictionary`
in your config file to its path. A data dictionary tells you which tables and fields exist and what
they actually mean — guessing at column semantics is the most common way these analyses go wrong.
If no dictionary is configured, inspect the schema directly and ask the user about any column whose
meaning isn't obvious from its name.

> **Worked example.** One setup this was built against used Snowflake as the warehouse and a
> licensed third-party workforce dataset (headcount, job postings, employee sentiment) as the
> source, with a hand-written dictionary mapping that vendor's tables to plain-English meanings.
> Neither the warehouse nor that dataset is required — it's simply the shape this works well in:
> a wide table of entities over time, plus a dictionary explaining the columns. The same skill has
> been run end-to-end on nothing but local CSVs.

**Iteration rule:** If the first query returns data but nothing is surprising or newsworthy, try a
different cut. Segment by cohort, time period, or category. Compare groups. Look for outliers. Run
up to 5 different queries before concluding the dataset doesn't have a story.

## Step 3: Apply Analytical Techniques

Select techniques based on the question. Always explain results in plain language — not just a number, but what it means.

### Descriptive & Exploratory (always run first)
- **Descriptive stats:** mean, median, percentiles (25th/75th/90th), standard deviation, IQR
- **Distribution analysis:** shape of the distribution, quartile breakdown, outlier count
- **Benchmarking:** where does an entity/cohort sit vs. the full distribution? ("top quartile", "below median")

```python
df.describe(percentiles=[.25, .5, .75, .9])
df['column'].quantile([0.25, 0.75])
```

### Time-Based Analysis
- **Trend analysis:** YoY, QoQ, MoM comparisons. Use rolling averages (e.g., 3-month) to smooth noise.
- **Cohort analysis:** group entities by start date, size band, or tier — compare the same metric across cohorts

```sql
-- YoY comparison (ANSI SQL — works on most warehouses)
SELECT
  DATE_TRUNC('year', date_col) AS year,
  AVG(metric) AS avg_metric,
  AVG(metric) / LAG(AVG(metric)) OVER (ORDER BY DATE_TRUNC('year', date_col)) - 1 AS yoy_change
FROM table
GROUP BY 1
ORDER BY 1
```

```python
# pandas equivalent
yearly = df.groupby(df['date_col'].dt.year)['metric'].mean()
yoy = yearly.pct_change()
```

### Comparative Analysis
- **Segment comparison:** split by size, cohort, category, value band — find which segments behave differently
- **Statistical significance (t-test):** confirm differences between groups aren't noise

```python
from scipy import stats
group_a = df[df['cohort'] == 'A']['metric']
group_b = df[df['cohort'] == 'B']['metric']
t_stat, p_value = stats.ttest_ind(group_a, group_b)
# p_value < 0.05 = statistically significant difference
print(f"p-value: {p_value:.4f} — {'significant' if p_value < 0.05 else 'not significant'}")
```

- **Chi-square test:** for comparing categorical distributions across groups

```python
from scipy.stats import chi2_contingency
contingency_table = pd.crosstab(df['cohort'], df['outcome'])
chi2, p_val, dof, expected = chi2_contingency(contingency_table)
```

- **Concentration analysis:** Gini coefficient, top-N% share

```python
# Top 10% share
top_10_pct = df['metric'].quantile(0.9)
top_share = df[df['metric'] >= top_10_pct]['metric'].sum() / df['metric'].sum()
print(f"Top 10% account for {top_share:.0%} of total")
```

### Relationship & Prediction (use Python — not SQL)
- **Correlation:** Pearson (linear) or Spearman (non-linear/ranked)

```python
pearson_r = df['var_a'].corr(df['var_b'])  # Pearson
spearman_r = df['var_a'].corr(df['var_b'], method='spearman')  # Spearman
print(f"Pearson r={pearson_r:.3f}, Spearman r={spearman_r:.3f}")
# Interpret: |r| > 0.7 = strong, 0.4-0.7 = moderate, < 0.4 = weak
```

- **Linear regression:** quantify trend direction and strength

```python
from sklearn.linear_model import LinearRegression
import numpy as np
X = df[['predictor_col']].values
y = df['outcome_col'].values
model = LinearRegression().fit(X, y)
r_squared = model.score(X, y)
print(f"R²={r_squared:.3f} — predictor explains {r_squared:.0%} of variance in outcome")
```

- **Random Forest:** when you need feature importance ("which variables predict X most?")

```python
from sklearn.ensemble import RandomForestRegressor  # or RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pandas as pd

# Prepare features (encode categoricals)
feature_cols = ['col1', 'col2', 'col3']  # replace with actual columns
X = df[feature_cols].copy()
for col in X.select_dtypes(include='object').columns:
    X[col] = LabelEncoder().fit_transform(X[col].astype(str))

y = df['target_col']

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

importance_df = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print(importance_df)
```

- **XGBoost:** use instead of Random Forest when Random Forest shows weak signal, the dataset is large (>10K rows), or the data has many missing values

```python
import xgboost as xgb
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = xgb.XGBRegressor(n_estimators=100, random_state=42, verbosity=0)  # or XGBClassifier
model.fit(X_train, y_train)

importance_df = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print(f"R² on test set: {model.score(X_test, y_test):.3f}")
print(importance_df)
```

### Anomaly Detection
- **Z-score outliers:** flag records more than 2 standard deviations from the mean

```python
from scipy import stats
import numpy as np
df['z_score'] = np.abs(stats.zscore(df['metric'].dropna()))
outliers = df[df['z_score'] > 2].sort_values('z_score', ascending=False)
print(f"{len(outliers)} outliers found ({len(outliers)/len(df):.1%} of dataset)")
```

- **IQR outliers:** more robust to extreme skew

```python
Q1, Q3 = df['metric'].quantile([0.25, 0.75])
IQR = Q3 - Q1
outliers = df[(df['metric'] < Q1 - 1.5*IQR) | (df['metric'] > Q3 + 1.5*IQR)]
```

## Step 3.5: Walk the User Through the Data

Before forming findings or narrative angles, **show the user the raw summary tables** across all cohorts/time periods. Present complete data, not cherry-picked comparisons. Walk through what you see and ask what stands out to them.

**Rules for presenting data:**
- Always show the full trajectory (every cohort, every period). Never compare only two time periods without showing everything in between.
- Present both absolute numbers and normalized metrics (e.g., both "units added" and "units per dollar"). Explain why both matter.
- Include percentile distributions (P10, P25, median, P75, P90) when showing entity-level metrics, not just medians.

## Step 4: Find 3-5 Headline Findings

Every headline finding must:
- Contain a specific number or percentage
- Be an observation about what the data shows, not an argument for a thesis
- Be explainable in one sentence

**Good:** "Widget shipments from the Northeast region fell 34% between Q1 and Q3, while every other region grew"
**Bad:** "Widget shipments have changed regionally"

*(Illustrative example only — invented numbers.)*

**Presentation rule:** Always show the full data table alongside the finding. Call out specific cohorts or comparisons as "Notable" callouts beneath the table, not as the finding itself. The finding is the trend; the callout highlights interesting points within it.

Don't stop at the first interesting number. Push to find at least 3 findings before writing the document.

## Step 5: Propose Narrative Angles

Based on the findings, propose 2-3 story angles — what article could this data support? For each angle:
- Name it ("The over-hiring trap", "AI's uneven distribution")
- Describe the story in 1-2 sentences
- Note which findings it draws on

## Step 6: Save the Findings Document

Save to: `{output_dir}/YYYY-MM-DD-<topic>/findings.md`, where `{output_dir}` comes from your config file.

Use this exact structure:

```
## Dataset Summary
- Source: [table name / CSV filename / vendor]
- Time period: [date range]
- Sample size: [N entities / records]
- Tables or files queried: [list]

## Headline Findings
1. [Quantified finding — specific number, surprising]
2. [Quantified finding]
3. [Quantified finding]
(up to 5)

## Anomalies & Surprises
- [Anything that contradicted expectations or can't easily be explained]

## Narrative Angles
1. **[Angle name]** — [1-2 sentences: the story and why it's interesting]
2. **[Angle name]** — [...]
3. **[Angle name]** — [...]

## Suggested Charts
- Finding 1 → [bar/line/scatter/horizontal bar/distribution] showing [what specifically]
- Finding 2 → [chart type] showing [what]
(one per major finding)

## Raw Summary Tables
[Paste key aggregated outputs from queries here]
```

## Step 7: Save the Reproducibility Kit (MANDATORY)

Every number in findings.md must be traceable to code and data on disk — not to a
conversation. Before declaring the analysis complete, create an `analysis/` folder
inside the story folder:

```
<story-folder>/analysis/
  queries/NN_name.sql    every query that produced a findings number, verbatim, with a
                         header comment: what it computes, params to edit on refresh,
                         and 2-3 validation values ("returns X for cohort Y")
  results/*.csv          the query outputs this findings.md was built from
  run_queries.py         reruns all queries against the configured source
  fetch_*.py             any external series (public APIs etc.) fetched by script into
                         results/, never hand-typed into prose or charts
  compute.py             ALL downstream computation (stats, models, adjustments, derived
                         series) as one deterministic, stdlib-preferred script that reads
                         results/*.csv and writes computed.json. Include a --validate flag
                         asserting the headline numbers so pipeline drift is caught.
  README.md              refresh runbook + known data traps
```

If the source is CSV rather than a database, `queries/` holds the pandas transformations
instead — same rule, same header comments.

Rules:
- **Code over agents.** Scratchpad prototyping is fine while exploring, but every
  computation that survives into findings.md gets promoted into `compute.py` before the
  story ships. If the session ended right now, someone must be able to reproduce every
  number by running the kit.
- Queries run interactively during exploration must be saved to `queries/` at the moment
  they produce a keeper number, not reconstructed later.
- If charts are published to a hosted chart service, keep a `chart_ids.json` and an
  `update_charts.py` that PUTs refreshed data to the EXISTING chart ids — published embeds
  then update automatically on republish.
- A worked reference kit ships in this repo at `examples/analysis/`.

## Next Step

When the findings document AND the reproducibility kit are saved, tell the user:
"Analysis complete. Findings saved to `[path]`; reproducibility kit in `[path]/analysis/`
(validated with compute.py --validate). When you're ready to write the article, run
`/write-story`."
