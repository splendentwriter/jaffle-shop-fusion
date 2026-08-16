"""Thin pass-throughs over the customer experience marts. No business logic here."""

from utils.bigquery import run_query
from utils.config import ANALYTICS_DATASET, PROJECT_ID


def get_reviews():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_reviews`")


def get_support_tickets():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_support`")
