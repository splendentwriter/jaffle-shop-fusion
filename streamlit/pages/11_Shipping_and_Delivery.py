"""Shipping & Delivery — carrier performance and on-time rate."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from queries.operations import get_shipping_delivery
from utils.config import APP_ICON, APP_TITLE
from utils.formatting import fmt_num, fmt_pct

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title("🚚 Shipping & Delivery")

shipments = get_shipping_delivery()
delivered = shipments[shipments["is_delivered"]]

kpi_row(
    [
        {"label": "Shipments", "value": fmt_num(len(shipments))},
        {"label": "Delivered", "value": fmt_pct(shipments["is_delivered"].mean())},
        {
            "label": "On-Time Rate",
            "value": fmt_pct(1 - delivered["was_late"].mean()) if len(delivered) else "—",
        },
        {"label": "Avg Hours to Deliver", "value": fmt_num(delivered["hours_to_deliver"].mean())},
    ]
)

st.subheader("Carrier performance")
by_carrier = (
    shipments.groupby("carrier_name")
    .agg(
        shipments=("shipment_id", "count"),
        delivered=("is_delivered", "sum"),
        late=("was_late", "sum"),
        avg_hours_to_deliver=("hours_to_deliver", "mean"),
        avg_delivery_attempts=("delivery_attempt_count", "mean"),
    )
    .reset_index()
)
fig = px.bar(
    by_carrier,
    x="carrier_name",
    y="avg_hours_to_deliver",
    labels={"carrier_name": "Carrier", "avg_hours_to_deliver": "Avg Hours to Deliver"},
)
st.plotly_chart(fig, width="stretch")

st.dataframe(
    by_carrier[["carrier_name", "shipments", "delivered", "late", "avg_hours_to_deliver", "avg_delivery_attempts"]].rename(
        columns={
            "carrier_name": "Carrier",
            "shipments": "Shipments",
            "delivered": "Delivered",
            "late": "Late",
            "avg_hours_to_deliver": "Avg Hours to Deliver",
            "avg_delivery_attempts": "Avg Delivery Attempts",
        }
    ),
    width="stretch",
    hide_index=True,
)

st.subheader("Status breakdown")
status_counts = shipments["status"].value_counts().reset_index()
status_counts.columns = ["Status", "Count"]
st.dataframe(status_counts, width="stretch", hide_index=True)
