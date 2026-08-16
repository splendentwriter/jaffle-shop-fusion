"""Jaffle Shop — Executive Overview.

Landing page of the analytics command center. Pulls directly from
mart_ecommerce_kpis and mart_sales_performance — all business logic
(revenue, margin, conversion, on-time delivery, etc.) is computed in dbt;
this file only renders it. See CONVENTIONS.md in the repo root.
"""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from queries.sales import get_ecommerce_kpis, get_sales_trend
from utils.config import APP_ICON, APP_TITLE
from utils.formatting import fmt_month, fmt_num, fmt_pct, fmt_usd

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title(f"{APP_ICON} Jaffle Shop")
st.caption("Executive Overview")

kpis = get_ecommerce_kpis()
trend = get_sales_trend()

if kpis is None:
    st.warning("No KPI data available yet.")
    st.stop()

st.info(
    f"Showing **{fmt_month(kpis['current_month'])}** vs **{fmt_month(kpis['prior_month'])}** "
    "— the two most recent complete months with order data. There's a real gap in the underlying "
    "history between the original seed data and the live streaming service's activity; see "
    "`models/marts/mart_ecommerce_kpis.yml` for why.",
    icon="ℹ️",
)

st.subheader("Headline metrics")
kpi_row(
    [
        {"label": "Net Revenue", "value": fmt_usd(kpis["net_revenue"]), "delta": kpis["revenue_change_pct"]},
        {"label": "Orders", "value": fmt_num(kpis["orders"]), "delta": kpis["orders_change_pct"]},
        {"label": "Customers", "value": fmt_num(kpis["customers"]), "delta": kpis["customers_change_pct"]},
        {
            "label": "Avg Order Value",
            "value": fmt_usd(kpis["avg_order_value"], decimals=2),
            "delta": kpis["avg_order_value_change_pct"],
        },
    ]
)

st.subheader("Funnel & operational health")
kpi_row(
    [
        {"label": "Checkout Conversion", "value": fmt_pct(kpis["checkout_conversion_rate"])},
        {"label": "Gross Margin", "value": fmt_pct(kpis["gross_margin_pct"])},
        {"label": "Refund Rate", "value": fmt_pct(kpis["refund_rate"])},
        {"label": "On-Time Delivery", "value": fmt_pct(kpis["on_time_delivery_rate"])},
    ]
)

st.subheader("Revenue trend")
fig = px.line(trend, x="month", y="revenue", markers=True)
fig.update_layout(yaxis_title="Revenue ($)", xaxis_title=None, height=400)
fig.update_yaxes(tickprefix="$", separatethousands=True)
st.plotly_chart(fig, width='stretch')

with st.expander("Monthly detail"):
    st.dataframe(
        trend[["month", "order_count", "customer_count", "revenue", "avg_order_value", "gross_margin_pct"]],
        width='stretch',
        hide_index=True,
    )

st.subheader("Business health")


def health_badge(condition_good: bool, condition_watch: bool) -> str:
    if condition_good:
        return "🟢 Strong"
    if condition_watch:
        return "🟡 Watch"
    return "🔴 Attention"


health_cols = st.columns(4)
health_cols[0].markdown(f"**Sales**  \n{health_badge(kpis['revenue_change_pct'] >= 0, kpis['revenue_change_pct'] >= -0.05)}")
health_cols[1].markdown(
    f"**Payments**  \n{health_badge(kpis['refund_rate'] < 0.05, kpis['refund_rate'] < 0.10)}"
)
health_cols[2].markdown(
    f"**Fulfillment**  \n{health_badge(kpis['on_time_delivery_rate'] >= 0.90, kpis['on_time_delivery_rate'] >= 0.75)}"
)
health_cols[3].markdown(
    f"**Inventory**  \n{health_badge(kpis['low_stock_sku_count'] == 0, kpis['low_stock_sku_count'] <= 3)}"
)

st.caption(
    "This is Loop 1 of the analytics command center (Executive Overview only) — "
    "Sales, Customers, Products, Operations, Finance, Marketing, and the other pages "
    "from the full spec come next, pending review of this page."
)
