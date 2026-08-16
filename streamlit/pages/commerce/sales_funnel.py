"""Sales Funnel — sessions through paid checkout, overall / by device / by channel."""

import plotly.graph_objects as go
import streamlit as st

from components.section_header import section_header
from queries.sales import get_session_funnel
from utils.formatting import fmt_num

section_header("Commerce", "Sales Funnel", "🔻")
st.caption(
    "Covers the smaller cart→checkout→payment funnel built on this session's web-behaviour data "
    "(separate from the larger historical order volume shown elsewhere — see CONVENTIONS.md)."
)

funnel = get_session_funnel()

STAGES = [
    ("Sessions", lambda df: len(df)),
    ("Product Views", lambda df: df["has_product_view"].sum()),
    ("Carts", lambda df: df["has_cart"].sum()),
    ("Checkouts", lambda df: df["has_checkout"].sum()),
    ("Paid", lambda df: df["is_paid"].sum()),
]

def funnel_chart(df, title):
    labels = [name for name, _ in STAGES]
    values = [int(fn(df)) for _, fn in STAGES]
    fig = go.Figure(
        go.Funnel(
            y=labels,
            x=values,
            textinfo="value+percent initial",
        )
    )
    fig.update_layout(title=title, height=420)
    return fig

st.subheader("Overall funnel")
st.plotly_chart(funnel_chart(funnel, "Sessions → Paid"), width="stretch")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Funnel by device")
    device = st.selectbox("Device", sorted(funnel["device_type"].unique()), key="device_filter")
    st.plotly_chart(funnel_chart(funnel[funnel["device_type"] == device], f"Device: {device}"), width="stretch")

with col2:
    st.subheader("Funnel by channel")
    channel = st.selectbox("Channel", sorted(funnel["referrer_source"].unique()), key="channel_filter")
    st.plotly_chart(
        funnel_chart(funnel[funnel["referrer_source"] == channel], f"Channel: {channel}"), width="stretch"
    )

st.subheader("Conversion by channel")
channel_summary = (
    funnel.groupby("referrer_source")
    .agg(sessions=("session_id", "count"), paid=("is_paid", "sum"))
    .reset_index()
)
channel_summary["conversion_rate"] = (channel_summary["paid"] / channel_summary["sessions"] * 100).round(1)
channel_summary = channel_summary.rename(
    columns={"referrer_source": "Channel", "sessions": "Sessions", "paid": "Paid", "conversion_rate": "Conversion %"}
)
st.dataframe(channel_summary, width="stretch", hide_index=True)
