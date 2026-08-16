"""Thin pass-throughs over the marketing marts. No business logic here."""

from utils.bigquery import run_query
from utils.config import ANALYTICS_DATASET, PROJECT_ID


def get_campaign_performance():
    return run_query(
        f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_campaign_performance` order by attributed_revenue desc"
    )


def get_attribution():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_attribution`")


def get_promotions():
    return run_query(
        f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_promotions` order by attributed_revenue desc"
    )
