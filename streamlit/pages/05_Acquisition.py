"""Customer Acquisition — customers and lifetime value by acquisition channel."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from queries.customers import get_customer_acquisition
from utils.config import APP_ICON, APP_TITLE
from utils.formatting import fmt_num, fmt_usd

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title("📥 Acquisition")
st.caption(
    "No real ad-spend data exists in this dataset, so CAC/ROAS aren't shown here — "
    "see Marketing → Campaign Performance for actual campaign spend."
)

acquisition = get_customer_acquisition()

kpi_row(
    [
        {"label": "Channels", "value": fmt_num(len(acquisition))},
        {"label": "Total Customers", "value": fmt_num(acquisition["customer_count"].sum())},
        {"label": "Total Revenue", "value": fmt_usd(acquisition["total_revenue"].sum())},
        {"label": "Avg Lifetime Value", "value": fmt_usd(acquisition["avg_lifetime_value"].mean(), decimals=2)},
    ]
)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Customers by channel")
    fig = px.bar(acquisition, x="acquisition_channel", y="customer_count")
    fig.update_layout(xaxis_title=None, yaxis_title="Customers", height=380)
    st.plotly_chart(fig, width="stretch")

with col2:
    st.subheader("Avg lifetime value by channel")
    fig = px.bar(acquisition.sort_values("avg_lifetime_value", ascending=False), x="acquisition_channel", y="avg_lifetime_value")
    fig.update_layout(xaxis_title=None, yaxis_title="Avg LTV ($)", height=380)
    st.plotly_chart(fig, width="stretch")

st.subheader("Detail")
st.dataframe(
    acquisition.rename(
        columns={
            "acquisition_channel": "Channel",
            "customer_count": "Customers",
            "total_revenue": "Total Revenue",
            "avg_lifetime_value": "Avg LTV",
        }
    ),
    width="stretch",
    hide_index=True,
)
