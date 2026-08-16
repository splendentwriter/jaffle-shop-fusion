"""Thin pass-throughs over the sales/KPI marts. dbt owns the business
logic (see models/marts/mart_ecommerce_kpis.sql and
models/marts/mart_sales_performance.sql) — these functions just select
from them, no aggregation or derivation happens here."""

from utils.bigquery import run_query
from utils.config import PROJECT_ID, ANALYTICS_DATASET


def get_ecommerce_kpis():
    df = run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_ecommerce_kpis`")
    return df.iloc[0] if not df.empty else None


def get_sales_trend():
    return run_query(
        f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_sales_performance` order by month"
    )
