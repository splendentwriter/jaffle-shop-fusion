"""Cross-domain alert counts for the Executive Command Center. Each query is
a thin count/filter over an existing mart — no business logic computed here."""

from utils.bigquery import run_query
from utils.config import ANALYTICS_DATASET, PROJECT_ID


def get_alert_summary():
    return run_query(
        f"""
        select
            (select count(*) from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_data_quality` where is_failing)
                as failing_tests,
            (select count(*) from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_inventory_health` where is_below_reorder_point)
                as low_stock_positions,
            (select count(*) from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_reconciliation` where not is_reconciled)
                as unreconciled_payouts,
            (select count(*) from `{PROJECT_ID}.{ANALYTICS_DATASET}.mart_support`
                where priority in ('high', 'urgent') and not is_resolved)
                as urgent_open_tickets
        """
    ).iloc[0]
