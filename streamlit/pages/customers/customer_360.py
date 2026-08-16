"""Customer 360 — segment overview + per-customer drill-down."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from components.section_header import section_header
from queries.customers import get_customer_360, get_customer_orders, get_customer_segments
from utils.formatting import fmt_num, fmt_usd

section_header("Customers", "Customer 360", "👥")

customer_360 = get_customer_360()
segments = get_customer_segments()

merged = customer_360.merge(segments[["customer_id", "segment"]], on="customer_id", how="left")

kpi_row(
    [
        {"label": "Total Customers", "value": fmt_num(len(merged))},
        {"label": "New (this segment run)", "value": fmt_num((merged["segment"] == "New").sum())},
        {
            "label": "Repeat Purchase Rate",
            "value": f"{(merged['count_lifetime_orders'] > 1).mean() * 100:.1f}%",
        },
        {"label": "Avg Lifetime Value", "value": fmt_usd(merged["lifetime_spend"].mean(), decimals=2)},
    ]
)

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("Segments")
    segment_counts = segments["segment"].value_counts().reset_index()
    segment_counts.columns = ["segment", "customers"]
    fig = px.bar(segment_counts, x="customers", y="segment", orientation="h")
    fig.update_layout(yaxis_title=None, height=380)
    fig.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig, width="stretch")

with col2:
    st.subheader("Customer value matrix")
    st.caption("Customers with at least one order — frequency/value are undefined for customers who never purchased.")
    purchasers = merged[merged["count_lifetime_orders"] > 0].copy()
    # BigQuery NUMERIC columns come back from pandas-gbq as python Decimal
    # objects (object dtype); plotly's numeric validators can't coerce
    # those for a size= encoding even though the values are numeric
    purchasers["lifetime_spend"] = purchasers["lifetime_spend"].astype(float)
    fig = px.scatter(
        purchasers,
        x="count_lifetime_orders",
        y="lifetime_spend",
        size="lifetime_spend",
        color="segment",
        hover_name="customer_name",
        labels={"count_lifetime_orders": "Purchase Frequency", "lifetime_spend": "Lifetime Value ($)"},
    )
    fig.update_layout(height=380)
    st.plotly_chart(fig, width="stretch")

st.subheader("Customer lookup")
customer_options = merged.sort_values("lifetime_spend", ascending=False)
selected_name = st.selectbox(
    "Search a customer",
    options=customer_options["customer_id"],
    format_func=lambda cid: f"{customer_options.set_index('customer_id').loc[cid, 'customer_name']} ({cid[:8]})",
)

if selected_name:
    record = merged[merged["customer_id"] == selected_name].iloc[0]
    st.markdown(f"### {record['customer_name']}")
    kpi_row(
        [
            {"label": "Orders", "value": fmt_num(record["count_lifetime_orders"])},
            {"label": "Lifetime Value", "value": fmt_usd(record["lifetime_spend"], decimals=2)},
            {"label": "Segment", "value": record["segment"] or "—"},
            {"label": "Support Tickets", "value": fmt_num(record["support_ticket_count"])},
        ]
    )
    st.caption(f"Acquisition channel: {record['acquisition_channel'] or 'unknown'} · Account status: {record['account_status'] or 'n/a'}")

    st.markdown("**Recent orders**")
    orders = get_customer_orders(selected_name)
    st.dataframe(orders, width="stretch", hide_index=True)
