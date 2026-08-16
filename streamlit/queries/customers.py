"""Thin pass-throughs over the customer marts. No business logic here —
segmentation, cohort math, and acquisition rollups all live in dbt."""

from utils.bigquery import run_query
from utils.config import ANALYTICS_DATASET, PROJECT_ID


def get_customer_360():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_customer_360`")


def get_customer_segments():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_customer_segments`")


def get_customer_acquisition():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_customer_acquisition`")


def get_retention_cohorts():
    return run_query(
        f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_customer_retention_cohorts` "
        "order by cohort_month, month_index"
    )


def get_customer_orders(customer_id: str, limit=50):
    return run_query(
        f"""
        select order_id, ordered_at, order_total, count_order_items
        from `{PROJECT_ID}.{ANALYTICS_DATASET}.orders`
        where customer_id = @customer_id
        order by ordered_at desc
        limit {int(limit)}
        """,
        params=(("customer_id", "STRING", customer_id),),
    )
