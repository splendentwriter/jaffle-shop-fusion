"""Payments — success/decline rates, chargebacks, and payment method mix."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from components.section_header import section_header
from queries.finance import get_payments
from utils.formatting import fmt_num, fmt_pct, fmt_usd

section_header("Finance", "Payments", "💳")

payments = get_payments()
for col in ["attempted_amount", "captured_amount", "refunded_amount", "net_amount"]:
    payments[col] = payments[col].astype(float)

kpi_row(
    [
        {"label": "Attempts", "value": fmt_num(len(payments))},
        {"label": "Success Rate", "value": fmt_pct(payments["is_successful"].mean())},
        {"label": "Captured Amount", "value": fmt_usd(payments["captured_amount"].sum())},
        {"label": "Chargebacks", "value": fmt_num(payments["has_chargeback"].sum())},
    ]
)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Payment method mix")
    method_counts = payments["method_type"].value_counts().reset_index()
    method_counts.columns = ["Method", "Count"]
    fig = px.pie(method_counts, names="Method", values="Count", hole=0.4)
    st.plotly_chart(fig, width="stretch")

with col2:
    st.subheader("Outcome breakdown")
    status_counts = payments["attempt_status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    fig = px.pie(status_counts, names="Status", values="Count", hole=0.4)
    st.plotly_chart(fig, width="stretch")

st.subheader("Decline reasons")
declines = payments[payments["is_declined"]]
if declines.empty:
    st.success("No declined payments.")
else:
    reason_counts = declines["decline_reason"].value_counts().reset_index()
    reason_counts.columns = ["Reason", "Count"]
    st.dataframe(reason_counts, width="stretch", hide_index=True)
