# Data Story Pipeline

Four Claude Code skills that take a dataset and produce a findings document, a long-form research article, charts, and a LinkedIn posting series — with a reproducibility kit so every number traces back to code.

```
/analyze-data ~/data/support-tickets.csv
```

## What it does

`analyze-data` explores a dataset, runs the appropriate statistical technique for the question, walks you through the full data before drawing conclusions, and writes a structured `findings.md` — quantified headline findings, anomalies, proposed narrative angles, and chart recommendations. It also writes an `analysis/` folder containing the queries, the raw results, and a `compute.py` that regenerates every number on demand.

`write-story` turns those findings into a long-form article (defaulting to *exploratory* structure rather than forcing a thesis the data doesn't support) plus matplotlib chart PNGs. It then hands off to `linkedin-schedule`, which decomposes the findings into a 3–7 post series with varied angles and hook patterns, and `linkedin-writer`, which formats each individual post.

The output is a folder per story:

```
2026-03-14-support-resolution/
  findings.md          article.md          charts/finding-1.png …
  linkedin-schedule.md linkedin-posts/01-hero-*.md …
  analysis/            queries/ results/ compute.py computed.json
```

## Who it's for

People who have data and need to publish something credible from it — analysts, operators, marketers, VCs, anyone running a data-driven content program. It assumes you can read a p-value but not that you want to hand-write the same cohort table for the fourth time.

It is most useful if you publish on a cadence and want each dataset to yield a full content series rather than one post. It is least useful if you want a single quick chart — that's more ceremony than the job needs.

You do **not** need a data warehouse. A CSV is a first-class input.

## What it costs

| Thing | Cost | Required? |
|---|---|---|
| Claude Code | Claude subscription | Yes |
| Python 3.9+ and `pip install -r requirements.txt` | Free | Yes |
| A data warehouse (Postgres, BigQuery, Snowflake, DuckDB…) | Whatever you already pay | Optional — CSV works |
| A licensed third-party dataset | Varies, often enterprise-priced | Optional |
| A hosted chart service | Varies | Optional — matplotlib PNGs are the default |

**No paid services are required.** The example in `examples/` runs on nothing but Python and the standard library, plus matplotlib for the chart.

## Install

```bash
git clone https://github.com/<owner>/data-story-pipeline.git
cd data-story-pipeline
cp -R skills/* ~/.claude/skills/
pip install -r requirements.txt
```

Copy **all four** skills. They form a chain: `analyze-data` → `write-story` → `linkedin-schedule` → `linkedin-writer`. Each one hands off to the next by name, so installing a subset leaves a step that references a skill you don't have.

Then create your config. The skills look for it at `~/.data-story-pipeline.json` first, falling back to `./config.json` in whatever directory you're working from:

```bash
cp config.example.json ~/.data-story-pipeline.json
```

```json
{
  "output_dir": "~/data-stories",
  "data_dictionary": null,
  "chart_color": "#2C5F8A",
  "cadence": "2x/week"
}
```

- **`output_dir`** — where story folders get written. The only setting you must change.
- **`data_dictionary`** — path to a file describing your source's tables and columns, if you have one. Leave `null` and the skill inspects the schema directly and asks about ambiguous columns.
- **`chart_color`** — primary color for all charts in an article.
- **`cadence`** — default LinkedIn posting rhythm.

No API keys. No environment variables.

Then in Claude Code:

```
/analyze-data ~/data/support-tickets.csv
```

## Example output

A complete worked example ships in [`examples/`](examples/), generated from synthetic data with a fixed seed. Every number in it is reproducible with `python3 examples/analysis/compute.py --validate`.

An excerpt from [`examples/findings.md`](examples/findings.md):

```markdown
## Headline Findings

1. **Median ticket resolution in the West improved 33.2% across cohorts — from
   12.3h in the 2022 cohort to 8.2h in 2025 — while the Northeast degraded 35.8%
   over the same window (6.6h to 8.9h).**

2. **The gap between the fastest and slowest region collapsed 82.5%, from 5.73
   hours in the 2022 cohort to 1.00 hour in 2025.**

## Anomalies & Surprises

- **The best-performing region is the only one getting materially worse.**
- **Convergence came from both directions at once.** It would be unremarkable if
  laggards simply caught up. Here the leader regressed toward the pack at nearly
  the same rate the laggard advanced.
```

See also [`examples/article.md`](examples/article.md) for the long-form output and [`examples/analysis/README.md`](examples/analysis/README.md) for the reproducibility kit.

## What it can't do

**It doesn't publish anywhere.** The private version this was extracted from pushed articles to Google Docs and the posting schedule to a task tracker with per-post reminders. Both were wired to bespoke CLI wrappers and are stripped here. You get markdown files and PNGs on disk. To add publishing back you'd need your own Google Cloud OAuth client and a Drive API upload step, or your tracker's API — the `scheduled_date` frontmatter field in each post file and the dated table in `linkedin-schedule.md` are the hooks to build against.

**It doesn't post to LinkedIn.** It writes post text to files. You copy and paste.

**It has no opinion about your data's correctness.** It will faithfully compute statistics on a column you've misunderstood. This is why `analyze-data` asks for a data dictionary and refuses to guess at ambiguous column semantics — but it can't catch an upstream pipeline that's been silently broken for a month.

**Statistical technique selection is a model judgment, not a proof.** The skill picks from a documented menu based on the question. It's a competent default, not a substitute for a statistician on anything consequential. It will report a correlation without establishing causation, and the article template is deliberately built to make you say so out loud.

**Small samples degrade quietly.** Nothing enforces a minimum cell size. A cohort grid with six companies per cell will produce percentiles that look authoritative and mean very little. Check your `n` per cell.

**LinkedIn guidance reflects a specific moment.** The cadence and hook-pattern advice in `linkedin-schedule` and `linkedin-writer` cites third-party analysis of B2B post performance. Platform behavior changes; treat it as a starting heuristic.

## How it works

These are Claude Code skills — structured instructions a model follows, not compiled software. You can read exactly what each one does in `skills/<name>/SKILL.md`, and you should, before trusting output from any of them.

1. **`analyze-data`** confirms scope with you, detects whether you're starting from data, a thesis, or a brief, connects to the source, and profiles it. It runs descriptive statistics first, then selects from a menu of techniques — t-tests, chi-square, correlation, regression, random forest / XGBoost feature importance, z-score and IQR outlier detection — based on the question. Before drawing conclusions it shows you the complete data across every cohort and period, because the fastest way to get a wrong story is to compare two cherry-picked points. Then it writes `findings.md` and the reproducibility kit.

2. **`write-story`** picks exploratory or thesis-driven structure (defaulting to exploratory), writes the article, and generates one chart per major finding under a fixed set of style rules — no chartjunk, labeled axes, source annotation on every chart.

3. **`linkedin-schedule`** maps findings, angles, and anomalies onto post types (hero, deep dive, contrarian, tactical, closer), builds a dated calendar with sequencing rules, and shows you the plan for approval before writing anything.

4. **`linkedin-writer`** formats each individual post.

Steps 3 and 4 both pause for your approval before generating. Step 1 pauses before querying.

## License

MIT — see [LICENSE](LICENSE).
