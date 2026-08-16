"""Reconciliation — payout batches vs. recomputed net of processing fees."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from queries.finance import get_reconciliation
from utils.config import APP_ICON, APP_TITLE
from utils.formatting import fmt_num, fmt_pct, fmt_usd

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title("🧾 Reconciliation")

payouts = get_reconciliation()
for col in ["payout_amount", "computed_net_amount", "discrepancy_amount"]:
    payouts[col] = payouts[col].astype(float)

kpi_row(
    [
        {"label": "Payouts", "value": fmt_num(len(payouts))},
        {"label": "Reconciled", "value": fmt_pct(payouts["is_reconciled"].mean())},
        {"label": "Total Payout Amount", "value": fmt_usd(payouts["payout_amount"].sum())},
        {
            "label": "Total Discrepancy",
            "value": fmt_usd(payouts.loc[~payouts["is_reconciled"], "discrepancy_amount"].abs().sum()),
        },
    ]
)

st.subheader("Payout amount vs. recomputed net")
fig = px.bar(
    payouts,
    x="period_start",
    y=["payout_amount", "computed_net_amount"],
    barmode="group",
    labels={"period_start": "Period", "value": "Amount", "variable": "Series"},
)
st.plotly_chart(fig, width="stretch")

st.subheader("Unreconciled payouts")
unreconciled = payouts[~payouts["is_reconciled"]]
if unreconciled.empty:
    st.success("All payouts reconciled within tolerance.")
else:
    st.dataframe(
        unreconciled[
            ["payout_id", "status", "period_start", "period_end", "payout_amount", "computed_net_amount", "discrepancy_amount"]
        ].rename(
            columns={
                "payout_id": "Payout ID",
                "status": "Status",
                "period_start": "Period Start",
                "period_end": "Period End",
                "payout_amount": "Payout Amount",
                "computed_net_amount": "Computed Net",
                "discrepancy_amount": "Discrepancy",
            }
        ),
        width="stretch",
        hide_index=True,
    )
