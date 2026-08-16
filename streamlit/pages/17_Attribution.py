"""Attribution — last-touch channel mix and time-to-convert."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from queries.marketing import get_attribution
from utils.config import APP_ICON, APP_TITLE
from utils.formatting import fmt_num, fmt_usd

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title("🎯 Attribution")

attribution = get_attribution()

if attribution.empty:
    st.info("No attributed checkouts yet — no marketing touch fell within 7 days of a completed checkout.")
else:
    attribution["attributed_revenue"] = attribution["attributed_revenue"].astype(float)

    kpi_row(
        [
            {"label": "Attributed Checkouts", "value": fmt_num(len(attribution))},
            {"label": "Channels", "value": fmt_num(attribution["channel"].nunique())},
            {"label": "Attributed Revenue", "value": fmt_usd(attribution["attributed_revenue"].sum())},
            {
                "label": "Avg Hours to Convert",
                "value": fmt_num(attribution["hours_between_touch_and_checkout"].mean()),
            },
        ]
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Revenue by channel")
        by_channel = attribution.groupby("channel")["attributed_revenue"].sum().reset_index()
        fig = px.pie(by_channel, names="channel", values="attributed_revenue", hole=0.4)
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Time to convert")
        fig = px.histogram(attribution, x="hours_between_touch_and_checkout", nbins=20)
        fig.update_layout(xaxis_title="Hours between touch and checkout", yaxis_title="Checkouts")
        st.plotly_chart(fig, width="stretch")

    st.subheader("Attributed checkouts")
    st.dataframe(
        attribution[
            ["checkout_id", "channel", "touch_at", "checkout_started_at", "hours_between_touch_and_checkout", "attributed_revenue"]
        ].rename(
            columns={
                "checkout_id": "Checkout ID",
                "channel": "Channel",
                "touch_at": "Touch At",
                "checkout_started_at": "Checkout Started",
                "hours_between_touch_and_checkout": "Hours to Convert",
                "attributed_revenue": "Attributed Revenue",
            }
        ),
        width="stretch",
        hide_index=True,
    )
