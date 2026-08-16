"""Orders — operational order-level detail with search/filter."""

import streamlit as st

from components.kpi_cards import kpi_row
from components.section_header import section_header
from queries.sales import get_orders
from utils.formatting import fmt_num, fmt_usd

section_header("Commerce", "Orders", "📋")
st.caption("Most recent 500 orders. Filter and search below.")

orders = get_orders(limit=500)

kpi_row(
    [
        {"label": "Orders (shown)", "value": fmt_num(len(orders))},
        {"label": "Total Value", "value": fmt_usd(orders["order_total"].sum())},
        {"label": "Avg Items / Order", "value": f"{orders['count_order_items'].mean():.1f}"},
        {"label": "First-Time Orders", "value": fmt_num((orders["customer_order_number"] == 1).sum())},
    ]
)

st.subheader("Search & filter")
col1, col2 = st.columns(2)
with col1:
    order_id_filter = st.text_input("Order ID contains")
with col2:
    customer_id_filter = st.text_input("Customer ID contains")

filtered = orders
if order_id_filter:
    filtered = filtered[filtered["order_id"].str.contains(order_id_filter, case=False, na=False)]
if customer_id_filter:
    filtered = filtered[filtered["customer_id"].str.contains(customer_id_filter, case=False, na=False)]

st.dataframe(
    filtered[
        [
            "order_id",
            "customer_id",
            "location_id",
            "ordered_at",
            "order_total",
            "count_order_items",
            "is_food_order",
            "is_drink_order",
            "customer_order_number",
        ]
    ],
    width="stretch",
    hide_index=True,
    height=500,
)
