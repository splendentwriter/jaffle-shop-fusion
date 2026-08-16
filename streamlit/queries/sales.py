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


def get_sales_by_location():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_sales_by_location`")


def get_sales_by_category():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_sales_by_category`")


def get_session_funnel():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_session_funnel`")


def get_orders(limit=500):
    return run_query(
        f"""
        select order_id, customer_id, location_id, ordered_at, order_total,
               count_order_items, is_food_order, is_drink_order, customer_order_number
        from `{PROJECT_ID}.{ANALYTICS_DATASET}.orders`
        order by ordered_at desc
        limit {limit}
        """
    )
