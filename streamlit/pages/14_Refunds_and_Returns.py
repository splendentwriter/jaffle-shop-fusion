"""Refunds & Returns — return reasons, refund turnaround, and resellability."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from queries.finance import get_refunds_returns
from utils.config import APP_ICON, APP_TITLE
from utils.formatting import fmt_num, fmt_pct, fmt_usd

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title("↩️ Refunds & Returns")

returns = get_refunds_returns()
returns["refund_amount"] = returns["refund_amount"].astype(float)

kpi_row(
    [
        {"label": "Returns", "value": fmt_num(len(returns))},
        {"label": "Refunded", "value": fmt_pct(returns["is_refunded"].mean())},
        {"label": "Refund Amount", "value": fmt_usd(returns["refund_amount"].sum())},
        {"label": "Avg Hours to Refund", "value": fmt_num(returns["hours_to_refund"].mean())},
    ]
)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Return reasons")
    reason_counts = returns["reason"].value_counts().reset_index()
    reason_counts.columns = ["Reason", "Count"]
    fig = px.bar(reason_counts, x="Reason", y="Count")
    st.plotly_chart(fig, width="stretch")

with col2:
    st.subheader("Status breakdown")
    status_counts = returns["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    fig = px.pie(status_counts, names="Status", values="Count", hole=0.4)
    st.plotly_chart(fig, width="stretch")

st.subheader("Items inspected but not resellable")
unsellable = returns[returns["has_unsellable_items"]]
st.caption(f"{fmt_num(len(unsellable))} returns had at least one inspected item that wasn't resellable.")
if not unsellable.empty:
    st.dataframe(
        unsellable[["return_id", "reason", "inspection_count", "resellable_count", "refund_amount"]].rename(
            columns={
                "return_id": "Return ID",
                "reason": "Reason",
                "inspection_count": "Inspected",
                "resellable_count": "Resellable",
                "refund_amount": "Refund Amount",
            }
        ),
        width="stretch",
        hide_index=True,
    )
