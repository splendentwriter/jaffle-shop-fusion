"""Promotions — coupon redemption volume, discount cost, and revenue impact."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from queries.marketing import get_promotions
from utils.config import APP_ICON, APP_TITLE
from utils.formatting import fmt_num, fmt_usd

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title("🏷️ Promotions")

promotions = get_promotions()
for col in ["total_discount_given", "attributed_revenue"]:
    promotions[col] = promotions[col].astype(float)

kpi_row(
    [
        {"label": "Promotions", "value": fmt_num(len(promotions))},
        {"label": "Redemptions", "value": fmt_num(promotions["redemption_count"].sum())},
        {"label": "Discount Given", "value": fmt_usd(promotions["total_discount_given"].sum())},
        {"label": "Attributed Revenue", "value": fmt_usd(promotions["attributed_revenue"].sum())},
    ]
)

st.subheader("Redemptions by promotion")
fig = px.bar(promotions, x="promotion_name", y="redemption_count", color="promotion_type")
st.plotly_chart(fig, width="stretch")

st.subheader("Promotion detail")
st.dataframe(
    promotions[
        ["promotion_name", "promotion_type", "redemption_count", "redeeming_customers", "total_discount_given", "attributed_revenue"]
    ].rename(
        columns={
            "promotion_name": "Promotion",
            "promotion_type": "Type",
            "redemption_count": "Redemptions",
            "redeeming_customers": "Customers",
            "total_discount_given": "Discount Given",
            "attributed_revenue": "Attributed Revenue",
        }
    ),
    width="stretch",
    hide_index=True,
)
