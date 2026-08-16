"""Thin pass-throughs over the product marts. No business logic here."""

from utils.bigquery import run_query
from utils.config import ANALYTICS_DATASET, PROJECT_ID


def get_product_performance():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_product_performance`")


def get_catalogue_health():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_catalogue_health`")
