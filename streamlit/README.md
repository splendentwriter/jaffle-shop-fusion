# Jaffle Shop Analytics Command Center (Streamlit)

Replaces the earlier Evidence.dev report. Currently: **Executive Overview
only** (loop 1 of the planned ~20-page build) — see `app.py`.

## Principle

**dbt owns business logic, Streamlit owns presentation.** Every number on
a page comes from a mart in `models/marts/` (e.g. `mart_ecommerce_kpis`,
`mart_sales_performance`) — pages and `queries/*.py` only select and
format, they never recompute a metric. See the repo root's
`CONVENTIONS.md`.

## Setup

```bash
cd streamlit
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Auth: same read-only `evidence-reporting` service account used previously
(`bigquery.dataViewer` + `bigquery.jobUser`, no write access). `.env`
(gitignored) already points at its key:

```
GOOGLE_APPLICATION_CREDENTIALS=/home/chibesa/.dbt/evidence-sa.json
```

## Run

```bash
.venv/bin/streamlit run app.py
```

## Structure

```
streamlit/
├── app.py              # Executive Overview (current landing/only page)
├── pages/               # future pages land here — Streamlit auto-discovers
│                         # files in this folder as additional nav items
├── components/          # reusable UI pieces (kpi_cards.py, ...)
├── queries/              # thin pass-throughs to marts, no business logic
└── utils/
    ├── bigquery.py       # cached BigQuery client + query runner
    ├── config.py         # project/dataset constants
    └── formatting.py     # display formatting only
```

## Known data characteristic

There's a real ~1-year gap in the `orders` history: the original seed data
ends August 2025, and the live streaming service's activity starts fresh
at "now" (currently August 2026) — nothing in between. The Executive
Overview's month-over-month comparison uses the two most recent *complete*
months with data, which today means Aug 2025 vs Jul 2025, not a real-time
current month. This is labelled explicitly on the page rather than hidden.
