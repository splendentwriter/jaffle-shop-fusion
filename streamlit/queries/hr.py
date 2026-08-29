"""Thin pass-through over the HR & Payroll mart. No business logic here."""

from utils.bigquery import run_query
from utils.config import ANALYTICS_DATASET, PROJECT_ID


def get_payroll():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_payroll`")
