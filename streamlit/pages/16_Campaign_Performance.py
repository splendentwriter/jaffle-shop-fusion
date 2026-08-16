"""Campaign Performance — attributed revenue and ROAS by campaign."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from queries.marketing import get_campaign_performance
from utils.config import APP_ICON, APP_TITLE
from utils.formatting import fmt_num, fmt_usd

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title("📣 Campaign Performance")

campaigns = get_campaign_performance()
for col in ["budget", "attributed_revenue", "roas"]:
    campaigns[col] = campaigns[col].astype(float)

kpi_row(
    [
        {"label": "Campaigns", "value": fmt_num(len(campaigns))},
        {"label": "Active", "value": fmt_num(campaigns["is_active"].sum())},
        {"label": "Total Budget", "value": fmt_usd(campaigns["budget"].sum())},
        {"label": "Attributed Revenue", "value": fmt_usd(campaigns["attributed_revenue"].sum())},
    ]
)

st.subheader("Revenue vs. budget by campaign")
fig = px.bar(
    campaigns,
    x="campaign_name",
    y=["budget", "attributed_revenue"],
    barmode="group",
    labels={"campaign_name": "Campaign", "value": "Amount", "variable": "Series"},
)
st.plotly_chart(fig, width="stretch")

st.subheader("Campaign detail")
st.dataframe(
    campaigns[
        ["campaign_name", "campaign_type", "budget", "attributed_checkouts", "attributed_customers", "attributed_revenue", "roas", "is_active"]
    ].rename(
        columns={
            "campaign_name": "Campaign",
            "campaign_type": "Type",
            "budget": "Budget",
            "attributed_checkouts": "Checkouts",
            "attributed_customers": "Customers",
            "attributed_revenue": "Attributed Revenue",
            "roas": "ROAS",
            "is_active": "Active",
        }
    ),
    width="stretch",
    hide_index=True,
)
