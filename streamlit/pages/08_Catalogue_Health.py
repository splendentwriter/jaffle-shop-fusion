"""Catalogue Health — completeness and stock status of the active catalogue."""

import streamlit as st

from components.kpi_cards import kpi_row
from queries.products import get_catalogue_health
from utils.config import APP_ICON, APP_TITLE
from utils.formatting import fmt_num, fmt_pct

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title("📋 Catalogue Health")

catalogue = get_catalogue_health()
total_skus = len(catalogue)

kpi_row(
    [
        {"label": "Total SKUs", "value": fmt_num(total_skus)},
        {"label": "Out of Stock", "value": fmt_num(catalogue["is_out_of_stock"].sum())},
        {"label": "Missing Description", "value": fmt_num((~catalogue["has_description"]).sum())},
        {"label": "Missing Image", "value": fmt_num((~catalogue["has_image"]).sum())},
    ]
)

st.caption(
    "Inventory is only tracked for the original seed catalogue — products added later by the live "
    "streaming service will show as out-of-stock because no inventory record exists yet, not because "
    "they sold out."
)

col1, col2 = st.columns(2)
with col1:
    st.metric("Description coverage", fmt_pct(catalogue["has_description"].mean()))
    st.metric("Brand coverage", fmt_pct(catalogue["has_brand"].mean()))
with col2:
    st.metric("Image coverage", fmt_pct(catalogue["has_image"].mean()))
    st.metric("Category coverage", fmt_pct(catalogue["has_category"].mean()))

st.subheader("Products needing attention")
issues = catalogue[
    ~catalogue["has_description"]
    | ~catalogue["has_image"]
    | ~catalogue["has_brand"]
    | ~catalogue["has_category"]
    | catalogue["is_out_of_stock"]
    | catalogue["is_missing_price"]
].copy()

if issues.empty:
    st.success("No catalogue issues found.")
else:
    st.dataframe(
        issues[
            [
                "product_name",
                "product_type",
                "has_description",
                "has_image",
                "has_brand",
                "has_category",
                "is_out_of_stock",
                "is_missing_price",
            ]
        ].rename(
            columns={
                "product_name": "Product",
                "product_type": "Type",
                "has_description": "Has Description",
                "has_image": "Has Image",
                "has_brand": "Has Brand",
                "has_category": "Has Category",
                "is_out_of_stock": "Out of Stock",
                "is_missing_price": "Missing Price",
            }
        ),
        width="stretch",
        hide_index=True,
    )
