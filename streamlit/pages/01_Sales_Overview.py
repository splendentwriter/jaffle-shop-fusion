"""Sales Overview — revenue trend, by location, by category."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from queries.sales import get_ecommerce_kpis, get_sales_by_category, get_sales_by_location, get_sales_trend
from utils.config import APP_ICON, APP_TITLE
from utils.formatting import fmt_num, fmt_pct, fmt_usd

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title("💰 Sales Overview")

kpis = get_ecommerce_kpis()
trend = get_sales_trend()
by_location = get_sales_by_location()
by_category = get_sales_by_category()

kpi_row(
    [
        {"label": "Net Revenue", "value": fmt_usd(kpis["net_revenue"]), "delta": kpis["revenue_change_pct"]},
        {"label": "Orders", "value": fmt_num(kpis["orders"]), "delta": kpis["orders_change_pct"]},
        {
            "label": "Avg Order Value",
            "value": fmt_usd(kpis["avg_order_value"], decimals=2),
            "delta": kpis["avg_order_value_change_pct"],
        },
        {"label": "Gross Margin", "value": fmt_pct(kpis["gross_margin_pct"])},
    ]
)

st.subheader("Revenue over time")
fig = px.line(trend, x="month", y="revenue", markers=True)
fig.update_layout(yaxis_title="Revenue ($)", xaxis_title=None, height=380)
fig.update_yaxes(tickprefix="$", separatethousands=True)
st.plotly_chart(fig, width="stretch")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Revenue by location")
    fig = px.bar(by_location.head(10), x="revenue", y="location_name", orientation="h")
    fig.update_layout(yaxis_title=None, xaxis_title="Revenue ($)", height=380)
    fig.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig, width="stretch")

with col2:
    st.subheader("Revenue by category")
    fig = px.pie(by_category, names="category", values="revenue", hole=0.4)
    fig.update_layout(height=380)
    st.plotly_chart(fig, width="stretch")

st.subheader("Monthly detail")
st.dataframe(
    trend[["month", "order_count", "customer_count", "revenue", "avg_order_value", "gross_margin_pct"]],
    width="stretch",
    hide_index=True,
)
