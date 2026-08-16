"""Executive Overview — broader trend view across revenue, customers,
profitability, operations, and marketing. Composes existing marts only;
no new business logic is computed here — see CONVENTIONS.md."""

import plotly.express as px
import streamlit as st

from components.section_header import section_header
from queries.finance import get_revenue_profitability
from queries.marketing import get_campaign_performance
from queries.operations import get_fulfillment_performance, get_shipping_delivery
from queries.sales import get_sales_trend
from utils.formatting import fmt_num, fmt_pct, fmt_usd

section_header("Executive", "Overview", "📊")

trend = get_sales_trend()
profitability = get_revenue_profitability()
fulfillment = get_fulfillment_performance()
shipping = get_shipping_delivery()
campaigns = get_campaign_performance()
for col in ["gross_revenue", "net_revenue", "net_margin_pct"]:
    profitability[col] = profitability[col].astype(float)
for col in ["attributed_revenue", "roas"]:
    campaigns[col] = campaigns[col].astype(float)

st.subheader("Revenue & order trend")
col1, col2 = st.columns(2)
with col1:
    fig = px.line(trend, x="month", y="revenue", markers=True, title="Revenue")
    fig.update_yaxes(tickprefix="$", separatethousands=True)
    fig.update_layout(height=340, xaxis_title=None)
    st.plotly_chart(fig, width="stretch")
with col2:
    fig = px.line(trend, x="month", y="order_count", markers=True, title="Orders")
    fig.update_layout(height=340, xaxis_title=None, yaxis_title="Orders")
    st.plotly_chart(fig, width="stretch")

st.subheader("Customer growth")
fig = px.bar(trend, x="month", y="customer_count")
fig.update_layout(height=320, yaxis_title="Active Customers", xaxis_title=None)
st.plotly_chart(fig, width="stretch")

st.subheader("Profitability trend")
fig = px.line(profitability, x="month", y=["gross_revenue", "net_revenue"], markers=True)
fig.update_layout(height=340, yaxis_title="Revenue ($)", xaxis_title=None, legend_title=None)
fig.update_yaxes(tickprefix="$", separatethousands=True)
st.plotly_chart(fig, width="stretch")

st.subheader("Operational performance")
shipped = fulfillment[fulfillment["is_shipped"]]
delivered = shipping[shipping["is_delivered"]]
op_cols = st.columns(3)
op_cols[0].metric("Fulfillment Shipped Rate", fmt_pct(fulfillment["is_shipped"].mean()))
op_cols[1].metric(
    "On-Time Delivery", fmt_pct(1 - delivered["was_late"].mean()) if len(delivered) else "—"
)
op_cols[2].metric("Avg Hours to Ship", fmt_num(shipped["hours_to_ship"].mean()) if len(shipped) else "—")

st.subheader("Marketing performance")
active_campaigns = campaigns[campaigns["is_active"]]
mkt_cols = st.columns(3)
mkt_cols[0].metric("Active Campaigns", fmt_num(len(active_campaigns)))
mkt_cols[1].metric("Attributed Revenue", fmt_usd(campaigns["attributed_revenue"].sum()))
mkt_cols[2].metric(
    "Avg ROAS (Active)", f"{active_campaigns['roas'].mean():.2f}x" if len(active_campaigns) else "—"
)
st.dataframe(
    campaigns[["campaign_name", "campaign_type", "attributed_revenue", "roas", "is_active"]].rename(
        columns={
            "campaign_name": "Campaign",
            "campaign_type": "Type",
            "attributed_revenue": "Attributed Revenue",
            "roas": "ROAS",
            "is_active": "Active",
        }
    ),
    width="stretch",
    hide_index=True,
)
