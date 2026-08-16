"""Thin pass-throughs over the finance marts. No business logic here."""

from utils.bigquery import run_query
from utils.config import ANALYTICS_DATASET, PROJECT_ID


def get_revenue_profitability():
    return run_query(
        f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_revenue_profitability` order by month"
    )


def get_payments():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_payments`")


def get_refunds_returns():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_refunds_returns`")


def get_reconciliation():
    return run_query(
        f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_reconciliation` order by period_start"
    )
