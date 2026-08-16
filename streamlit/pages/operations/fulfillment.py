"""Fulfillment — pick/pack/ship funnel performance."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from components.section_header import section_header
from queries.operations import get_fulfillment_performance
from utils.formatting import fmt_num, fmt_pct

section_header("Operations", "Fulfillment", "🏭")

fulfillment = get_fulfillment_performance()
shipped = fulfillment[fulfillment["is_shipped"]]

kpi_row(
    [
        {"label": "Fulfillment Orders", "value": fmt_num(len(fulfillment))},
        {"label": "Shipped", "value": fmt_pct(fulfillment["is_shipped"].mean())},
        {"label": "Cancelled", "value": fmt_pct(fulfillment["is_cancelled"].mean())},
        {"label": "Avg Hours to Ship", "value": fmt_num(shipped["hours_to_ship"].mean())},
    ]
)

st.subheader("Pick/pack time by warehouse")
by_warehouse = (
    fulfillment.groupby("warehouse_name")
    .agg(
        orders=("fulfillment_order_id", "count"),
        avg_picking_minutes=("picking_minutes", "mean"),
        avg_packing_minutes=("packing_minutes", "mean"),
        avg_hours_to_ship=("hours_to_ship", "mean"),
    )
    .reset_index()
)
fig = px.bar(
    by_warehouse,
    x="warehouse_name",
    y=["avg_picking_minutes", "avg_packing_minutes"],
    barmode="group",
    labels={"warehouse_name": "Warehouse", "value": "Minutes", "variable": "Stage"},
)
st.plotly_chart(fig, width="stretch")

st.subheader("Warehouse summary")
st.dataframe(
    by_warehouse.rename(
        columns={
            "warehouse_name": "Warehouse",
            "orders": "Orders",
            "avg_picking_minutes": "Avg Picking (min)",
            "avg_packing_minutes": "Avg Packing (min)",
            "avg_hours_to_ship": "Avg Hours to Ship",
        }
    ),
    width="stretch",
    hide_index=True,
)

st.subheader("Status breakdown")
status_counts = fulfillment["status"].value_counts().reset_index()
status_counts.columns = ["Status", "Count"]
st.dataframe(status_counts, width="stretch", hide_index=True)
