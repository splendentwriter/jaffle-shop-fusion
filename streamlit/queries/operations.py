"""Thin pass-throughs over the operations marts. No business logic here."""

from utils.bigquery import run_query
from utils.config import ANALYTICS_DATASET, PROJECT_ID


def get_inventory_health():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_inventory_health`")


def get_fulfillment_performance():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_fulfillment_performance`")


def get_shipping_delivery():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_shipping_delivery`")
