# Jaffle Shop Analytics Command Center (Streamlit)

Replaces the earlier Evidence.dev report. A 27-page app organized around
how an e-commerce business actually operates — Executive, Commerce,
Customers, Products, Operations, Finance, Marketing, Customer Experience,
HR & Payroll, and Data Platform — via `st.navigation()` with top-position,
grouped nav in `app.py`.

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

## Auth

Same read-only `evidence-reporting` service account used previously
(`bigquery.dataViewer` + `bigquery.jobUser`, no write access), but via
**Streamlit Secrets** rather than a `GOOGLE_APPLICATION_CREDENTIALS` file
path — this is Streamlit's official pattern for BigQuery
(`st.secrets["gcp_service_account"]` +
`service_account.Credentials.from_service_account_info()`), and it's what
lets the exact same code run locally and on Streamlit Community Cloud.

**Local**: `.streamlit/secrets.toml` (gitignored, never committed) —
already set up, contains a `[gcp_service_account]` table with the service
account key's fields (`type`, `project_id`, `private_key`, `client_email`,
etc. — the same fields as the raw JSON key, just as TOML).

**Streamlit Community Cloud**: paste the same TOML content into
**App → Settings → Secrets**, not into GitHub. The repo stays the source
of truth for the app/dbt/generator code; the credentials never enter it.

## Run

```bash
.venv/bin/streamlit run app.py
```

## Structure

```
streamlit/
├── app.py                    # nav shell: builds st.Page()s, groups them into
│                              # business sections, position="top", pg.run()
├── pages/
│   ├── executive/             # Command Center (landing/default), Overview
│   ├── commerce/               # Sales Overview, Sales Funnel, Orders, Promotions
│   ├── customers/               # Customer 360, Acquisition, Retention
│   ├── products/                 # Product Performance, Catalogue Health
│   ├── operations/                # Inventory, Fulfillment, Shipping & Delivery
│   ├── finance/                     # Payments, Revenue & Profitability,
│   │                                 # Returns & Refunds, Reconciliation
│   ├── marketing/                    # Campaign Performance, Attribution
│   ├── customer_experience/           # Reviews, Support
│   ├── hr/                             # Employees, Payroll
│   └── data_platform/                   # Data Quality, Pipeline Health,
│                                          # Model Performance
├── components/          # reusable UI pieces (kpi_cards, section_header,
│                         # status_badge, insight_card, data_table, charts,
│                         # filters)
├── queries/              # thin pass-throughs to marts, no business logic
└── utils/
    ├── bigquery.py       # cached BigQuery client + query runner
    ├── config.py         # project/dataset constants
    └── formatting.py     # display formatting only
```

Individual page files don't call `st.set_page_config()` — that's set once
in `app.py`, which is why every page file was edited to drop that line (a
navigation-layer change, not a business-logic one) when this was
restructured from Streamlit's old flat `pages/` auto-discovery into
grouped `st.navigation()`. Each page opens with a
`section_header("Section", "Page Title", "icon")` call instead of a bare
`st.title()`, so the business section a page belongs to is always visible
even without looking at the nav bar.

## Known data characteristic

There's a real ~1-year gap in the `orders` history: the original seed data
ends August 2025, and the live streaming service's activity starts fresh
at "now" (currently August 2026) — nothing in between. The Executive
Overview's month-over-month comparison uses the two most recent *complete*
months with data, which today means Aug 2025 vs Jul 2025, not a real-time
current month. This is labelled explicitly on the Executive Command Center
page rather than hidden.
