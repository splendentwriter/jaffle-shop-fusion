"""Product Performance — top products, margin/volume scatter."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from queries.products import get_product_performance
from utils.config import APP_ICON, APP_TITLE
from utils.formatting import fmt_num, fmt_pct, fmt_usd

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title("🛍️ Product Performance")

products = get_product_performance()
# BigQuery NUMERIC columns arrive as Decimal (object dtype); plotly's
# numeric size/axis encodings need real floats
for col in ["revenue", "margin_pct", "total_supply_cost"]:
    products[col] = products[col].astype(float)

kpi_row(
    [
        {"label": "Products Sold", "value": fmt_num(len(products))},
        {"label": "Total Revenue", "value": fmt_usd(products["revenue"].sum())},
        {"label": "Total Units", "value": fmt_num(products["units_sold"].sum())},
        {"label": "Avg Margin", "value": fmt_pct(products["margin_pct"].mean())},
    ]
)

st.subheader("Top products by revenue")
top20 = products.head(20)
st.dataframe(
    top20[["product_name", "revenue", "units_sold", "margin_pct", "average_rating"]].rename(
        columns={
            "product_name": "Product",
            "revenue": "Revenue",
            "units_sold": "Units",
            "margin_pct": "Margin",
            "average_rating": "Rating",
        }
    ),
    width="stretch",
    hide_index=True,
)

st.subheader("Volume vs. margin")
st.caption("Bubble size = revenue. Identifies high-volume/low-margin vs. low-volume/high-margin products.")
fig = px.scatter(
    products,
    x="units_sold",
    y="margin_pct",
    size="revenue",
    color="product_name",
    hover_name="product_name",
    labels={"units_sold": "Units Sold", "margin_pct": "Margin %"},
)
fig.update_yaxes(tickformat=".0%")
fig.update_layout(height=500, showlegend=False)
st.plotly_chart(fig, width="stretch")
