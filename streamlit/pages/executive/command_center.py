"""Executive Command Center — top-line KPIs, cross-domain alerts, business
health, and top opportunities/risks/trends at a glance. Composes existing
marts only; no new business logic is computed here — see CONVENTIONS.md."""

import streamlit as st

from components.insight_card import insight_card
from components.kpi_cards import kpi_row
from components.section_header import section_header
from components.status_badge import status_badge
from queries.alerts import get_alert_summary
from queries.finance import get_payments
from queries.marketing import get_campaign_performance
from queries.products import get_catalogue_health
from queries.sales import get_ecommerce_kpis
from utils.formatting import fmt_month, fmt_num, fmt_pct, fmt_usd

section_header("Executive", "Command Center", "🏠")

kpis = get_ecommerce_kpis()
if kpis is None:
    st.warning("No KPI data available yet.")
    st.stop()

alerts = get_alert_summary()
catalogue = get_catalogue_health()
payments = get_payments()
campaigns = get_campaign_performance()
for col in ["budget", "attributed_revenue", "roas"]:
    campaigns[col] = campaigns[col].astype(float)
active_campaigns = campaigns[campaigns["is_active"]]

catalogue_completeness_rate = (
    catalogue["has_description"] & catalogue["has_image"] & catalogue["has_brand"] & catalogue["has_category"]
).mean()
payment_success_rate = payments["is_successful"].mean()
avg_active_roas = active_campaigns["roas"].mean() if len(active_campaigns) else None

st.info(
    f"Showing **{fmt_month(kpis['current_month'])}** vs **{fmt_month(kpis['prior_month'])}** "
    "— the two most recent complete months with order data. There's a real gap in the underlying "
    "history between the original seed data and the live streaming service's activity; see "
    "`models/marts/mart_ecommerce_kpis.yml` for why.",
    icon="ℹ️",
)

st.subheader("Top-line metrics")
kpi_row(
    [
        {"label": "Revenue", "value": fmt_usd(kpis["net_revenue"]), "delta": kpis["revenue_change_pct"]},
        {"label": "Orders", "value": fmt_num(kpis["orders"]), "delta": kpis["orders_change_pct"]},
        {"label": "Customers", "value": fmt_num(kpis["customers"]), "delta": kpis["customers_change_pct"]},
    ]
)
kpi_row(
    [
        {
            "label": "Avg Order Value",
            "value": fmt_usd(kpis["avg_order_value"], decimals=2),
            "delta": kpis["avg_order_value_change_pct"],
        },
        {"label": "Checkout Conversion", "value": fmt_pct(kpis["checkout_conversion_rate"])},
        {"label": "Gross Margin", "value": fmt_pct(kpis["gross_margin_pct"])},
    ]
)

st.subheader("Attention needed")
alert_cols = st.columns(4)
alert_cols[0].metric("Failing Data Tests", fmt_num(alerts["failing_tests"]))
alert_cols[1].metric("Low Stock Positions", fmt_num(alerts["low_stock_positions"]))
alert_cols[2].metric("Unreconciled Payouts", fmt_num(alerts["unreconciled_payouts"]))
alert_cols[3].metric("Urgent Open Tickets", fmt_num(alerts["urgent_open_tickets"]))

st.subheader("Business health")
row1 = st.columns(4)
row1[0].markdown(f"**Sales**  \n{status_badge(kpis['revenue_change_pct'] >= 0, kpis['revenue_change_pct'] >= -0.05)}")
row1[1].markdown(
    f"**Customers**  \n{status_badge(kpis['customers_change_pct'] >= 0, kpis['customers_change_pct'] >= -0.05)}"
)
row1[2].markdown(
    f"**Products**  \n{status_badge(catalogue_completeness_rate >= 0.9, catalogue_completeness_rate >= 0.75)}"
)
row1[3].markdown(
    f"**Inventory**  \n{status_badge(kpis['low_stock_sku_count'] == 0, kpis['low_stock_sku_count'] <= 3)}"
)

row2 = st.columns(4)
row2[0].markdown(f"**Payments**  \n{status_badge(payment_success_rate >= 0.95, payment_success_rate >= 0.90)}")
row2[1].markdown(
    f"**Fulfillment**  \n{status_badge(kpis['on_time_delivery_rate'] >= 0.90, kpis['on_time_delivery_rate'] >= 0.75)}"
)
row2[2].markdown(
    f"**Marketing**  \n{status_badge((avg_active_roas or 0) >= 1, (avg_active_roas or 0) >= 0.5)}"
)
row2[3].markdown(f"**Returns**  \n{status_badge(kpis['refund_rate'] < 0.05, kpis['refund_rate'] < 0.10)}")

st.subheader("Top opportunities, risks & trends")
opp_col, risk_col, trend_col = st.columns(3)

with opp_col:
    st.markdown("**🚀 Opportunities**")
    shown = False
    if kpis["revenue_change_pct"] >= 0.05:
        insight_card(f"Revenue is up {fmt_pct(kpis['revenue_change_pct'])} month-over-month.", "success")
        shown = True
    if avg_active_roas and avg_active_roas >= 1.5:
        insight_card(f"Active campaigns are averaging {avg_active_roas:.1f}x ROAS.", "success")
        shown = True
    if not shown:
        st.caption("No standout opportunities flagged this period.")

with risk_col:
    st.markdown("**⚠️ Risks**")
    shown = False
    if kpis["refund_rate"] >= 0.05:
        insight_card(f"Refund rate is elevated at {fmt_pct(kpis['refund_rate'])}.", "warning")
        shown = True
    if alerts["low_stock_positions"] > 0:
        insight_card(f"{fmt_num(alerts['low_stock_positions'])} inventory positions are below reorder point.", "warning")
        shown = True
    if alerts["failing_tests"] > 0:
        insight_card(f"{fmt_num(alerts['failing_tests'])} data quality tests are failing.", "error")
        shown = True
    if alerts["unreconciled_payouts"] > 0:
        insight_card(f"{fmt_num(alerts['unreconciled_payouts'])} payouts are unreconciled.", "warning")
        shown = True
    if alerts["urgent_open_tickets"] > 0:
        insight_card(f"{fmt_num(alerts['urgent_open_tickets'])} urgent support tickets are still open.", "warning")
        shown = True
    if not shown:
        st.caption("No risks flagged this period.")

with trend_col:
    st.markdown("**📈 Trends**")
    insight_card(f"Orders {'up' if kpis['orders_change_pct'] >= 0 else 'down'} {fmt_pct(abs(kpis['orders_change_pct']))} MoM.", "info")
    insight_card(
        f"Customers {'up' if kpis['customers_change_pct'] >= 0 else 'down'} {fmt_pct(abs(kpis['customers_change_pct']))} MoM.",
        "info",
    )
    insight_card(f"On-time delivery at {fmt_pct(kpis['on_time_delivery_rate'])}.", "info")

st.caption("Drill into any business area via the navigation above.")
