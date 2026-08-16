"""Thin pass-throughs over the data platform (observability) marts. No business logic here."""

from utils.bigquery import run_query
from utils.config import ANALYTICS_DATASET, PROJECT_ID


def get_data_quality():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_data_quality`")


def get_pipeline_health(limit=100):
    return run_query(
        f"""
        select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_pipeline_health`
        order by started_at desc
        limit {int(limit)}
        """
    )


def get_model_performance(limit=2000):
    return run_query(
        f"""
        select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_model_performance`
        order by created_at desc
        limit {int(limit)}
        """
    )
