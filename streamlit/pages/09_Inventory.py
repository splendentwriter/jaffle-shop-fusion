"""Inventory — stock positions and reorder alerts."""

import streamlit as st

from components.kpi_cards import kpi_row
from queries.operations import get_inventory_health
from utils.config import APP_ICON, APP_TITLE
from utils.formatting import fmt_num, fmt_pct

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title("📦 Inventory")

inventory = get_inventory_health()

kpi_row(
    [
        {"label": "SKU / Warehouse Positions", "value": fmt_num(len(inventory))},
        {"label": "Below Reorder Point", "value": fmt_num(inventory["is_below_reorder_point"].sum())},
        {"label": "Total On Hand", "value": fmt_num(inventory["quantity_on_hand"].sum())},
        {"label": "Total Available", "value": fmt_num(inventory["available_quantity"].sum())},
    ]
)

regions = sorted(inventory["region"].dropna().unique())
selected_region = st.selectbox("Region", ["All"] + regions)
filtered = inventory if selected_region == "All" else inventory[inventory["region"] == selected_region]

st.subheader("Stock by warehouse")
by_warehouse = (
    filtered.groupby(["warehouse_name", "region"])
    .agg(
        skus=("product_id", "nunique"),
        on_hand=("quantity_on_hand", "sum"),
        available=("available_quantity", "sum"),
        below_reorder=("is_below_reorder_point", "sum"),
    )
    .reset_index()
    .rename(
        columns={
            "warehouse_name": "Warehouse",
            "region": "Region",
            "skus": "SKUs",
            "on_hand": "On Hand",
            "available": "Available",
            "below_reorder": "Below Reorder",
        }
    )
)
st.dataframe(by_warehouse, width="stretch", hide_index=True)

st.subheader("Reorder alerts")
alerts = filtered[filtered["is_below_reorder_point"]].sort_values("available_quantity")
if alerts.empty:
    st.success("No products below their reorder point.")
else:
    st.dataframe(
        alerts[
            ["product_name", "warehouse_name", "quantity_on_hand", "reorder_point", "available_quantity"]
        ].rename(
            columns={
                "product_name": "Product",
                "warehouse_name": "Warehouse",
                "quantity_on_hand": "On Hand",
                "reorder_point": "Reorder Point",
                "available_quantity": "Available",
            }
        ),
        width="stretch",
        hide_index=True,
    )

st.caption(f"{fmt_pct(len(alerts) / len(filtered) if len(filtered) else None)} of positions are below reorder point.")
