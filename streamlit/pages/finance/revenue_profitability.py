"""Revenue & Profitability — monthly gross/net revenue with fee and discount drag."""

import plotly.graph_objects as go
import streamlit as st

from components.kpi_cards import kpi_row
from components.section_header import section_header
from queries.finance import get_revenue_profitability
from utils.formatting import fmt_month, fmt_pct, fmt_usd

section_header("Finance", "Revenue & Profitability", "💰")

monthly = get_revenue_profitability()
numeric_cols = [
    "items_subtotal",
    "discount_amount",
    "refunded_amount",
    "processing_fee",
    "gross_revenue",
    "net_revenue",
    "net_margin_pct",
]
for col in numeric_cols:
    monthly[col] = monthly[col].astype(float)

latest = monthly.iloc[-1]

kpi_row(
    [
        {"label": f"Net Revenue ({fmt_month(latest['month'])})", "value": fmt_usd(latest["net_revenue"])},
        {"label": "Net Margin", "value": fmt_pct(latest["net_margin_pct"])},
        {"label": "Processing Fees", "value": fmt_usd(latest["processing_fee"])},
        {"label": "Refunds", "value": fmt_usd(latest["refunded_amount"])},
    ]
)

st.subheader("Gross vs. net revenue")
fig = go.Figure()
fig.add_trace(go.Bar(x=monthly["month"], y=monthly["gross_revenue"], name="Gross Revenue"))
fig.add_trace(go.Bar(x=monthly["month"], y=monthly["net_revenue"], name="Net Revenue"))
fig.update_layout(barmode="group", height=450)
st.plotly_chart(fig, width="stretch")

st.subheader("Where revenue goes")
fig2 = go.Figure()
for col, label in [
    ("discount_amount", "Discounts"),
    ("refunded_amount", "Refunds"),
    ("processing_fee", "Processing Fees"),
]:
    fig2.add_trace(go.Bar(x=monthly["month"], y=monthly[col], name=label))
fig2.update_layout(barmode="stack", height=400)
st.plotly_chart(fig2, width="stretch")

st.subheader("Monthly detail")
st.dataframe(
    monthly.rename(
        columns={
            "month": "Month",
            "checkout_count": "Checkouts",
            "items_subtotal": "Items Subtotal",
            "discount_amount": "Discounts",
            "refunded_amount": "Refunds",
            "processing_fee": "Processing Fees",
            "gross_revenue": "Gross Revenue",
            "net_revenue": "Net Revenue",
            "net_margin_pct": "Net Margin",
        }
    ),
    width="stretch",
    hide_index=True,
)
