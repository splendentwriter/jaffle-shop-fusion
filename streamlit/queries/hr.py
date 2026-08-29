"""Thin pass-throughs over the HR & Payroll marts. No business logic here."""

from utils.bigquery import run_query
from utils.config import ANALYTICS_DATASET, PROJECT_ID


def get_payroll():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_payroll`")


def get_employees():
    return run_query(f"select * from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_employees`")
