# Reproducibility kit — worked example

This is the reference implementation for the `analysis/` folder that `/analyze-data`
requires alongside every findings document. Copy this structure for real stories.

The principle: **every number in `findings.md` must be reproducible by running code in
this folder.** If the session that produced the analysis ended right now, someone else
should be able to regenerate every figure without asking a question.

## Refresh runbook

```bash
# 1. Regenerate the source data (in a real story: rerun the warehouse queries)
python3 queries/01_make_synthetic_source.py

# 2. Recompute everything and assert the headline numbers still hold
python3 compute.py --validate

# 3. Re-render charts from computed.json
pip install matplotlib          # only dependency outside the stdlib
python3 make_chart.py
```

If step 2 fails, **do not update the article to match the new numbers.** A validation
failure means either the source changed or the computation drifted, and you need to
know which before republishing anything.

## What each file is for

| File | Role |
|---|---|
| `queries/01_make_synthetic_source.py` | Produces the source data. In a real story this is `01_<name>.sql` — the verbatim warehouse query — or the pandas load for a CSV source. One file per query, numbered in execution order. |
| `results/companies.csv` | The query output the findings were built from. Committed so the analysis is reproducible even if the upstream source changes. |
| `compute.py` | All downstream computation: aggregation, percentiles, correlation, regression. Deterministic and stdlib-only. Writes `computed.json`. |
| `computed.json` | The numbers `findings.md` and `article.md` quote. The single source of truth for every figure in the prose. |
| `make_chart.py` | Renders charts from `computed.json`, never from hand-typed values. |

## Rules this kit demonstrates

1. **Query headers carry validation values.** Each query file states what it computes, which params to edit on refresh, and 2–3 known-good outputs. See the docstring in `queries/01_make_synthetic_source.py`.

2. **`compute.py --validate` asserts the headline numbers.** Pipeline drift breaks the build rather than silently changing the story. The assertions live in `validate_numbers()`.

3. **Charts read from `computed.json`.** No number is typed twice. If the computation changes, the chart changes with it on the next render.

4. **Prose quotes computed values only.** Both `findings.md` and `article.md` state up front that they are generated from this kit, and every figure in them appears in `computed.json`.

5. **Fixed seeds, no wall-clock dependencies.** Rerunning on a different machine on a different day produces byte-identical output.

## Known data traps in this example

- **Percentiles pool cohorts.** The within-region distribution table combines all four cohorts. A region that improved sharply will show an artificially wide P10–P90 spread as a result — the West's 7.10h spread partly reflects its own trajectory over time, not just company-to-company variation. Splitting by cohort would separate the two.

- **Medians of medians.** `median_resolution_hours` is already a per-company median; the region-cohort grid takes a median of those. That is intentional (it resists outlier companies) but it is not the same as the median ticket resolution time across all tickets, and shouldn't be described as such.

- **The relationships are synthetic.** Resolution time and CSAT correlate here because the generator makes them correlate. Never cite a number from this example as evidence about the real world.
