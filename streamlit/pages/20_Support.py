"""Support — ticket volume, resolution time, and reopen rate by team."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from queries.customer_experience import get_support_tickets
from utils.config import APP_ICON, APP_TITLE
from utils.formatting import fmt_num, fmt_pct

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title("🎧 Support")

tickets = get_support_tickets()
resolved = tickets[tickets["is_resolved"]]

kpi_row(
    [
        {"label": "Tickets", "value": fmt_num(len(tickets))},
        {"label": "Resolved", "value": fmt_pct(tickets["is_resolved"].mean())},
        {"label": "Reopened", "value": fmt_pct(tickets["was_reopened"].mean())},
        {"label": "Avg Hours to Resolve", "value": fmt_num(resolved["hours_to_resolve"].mean())},
    ]
)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Tickets by category")
    category_counts = tickets["category"].value_counts().reset_index()
    category_counts.columns = ["Category", "Count"]
    fig = px.bar(category_counts, x="Category", y="Count")
    st.plotly_chart(fig, width="stretch")

with col2:
    st.subheader("Tickets by priority")
    priority_counts = tickets["priority"].value_counts().reset_index()
    priority_counts.columns = ["Priority", "Count"]
    fig = px.pie(priority_counts, names="Priority", values="Count", hole=0.4)
    st.plotly_chart(fig, width="stretch")

st.subheader("Team performance")
by_team = (
    tickets[tickets["team"].notna()]
    .groupby("team")
    .agg(
        tickets=("ticket_id", "count"),
        resolved_rate=("is_resolved", "mean"),
        reopen_rate=("was_reopened", "mean"),
        avg_hours_to_resolve=("hours_to_resolve", "mean"),
    )
    .reset_index()
)
by_team["resolved_rate"] = (by_team["resolved_rate"] * 100).round(1)
by_team["reopen_rate"] = (by_team["reopen_rate"] * 100).round(1)
st.dataframe(
    by_team.rename(
        columns={
            "team": "Team",
            "tickets": "Tickets",
            "resolved_rate": "Resolved Rate (%)",
            "reopen_rate": "Reopen Rate (%)",
            "avg_hours_to_resolve": "Avg Hours to Resolve",
        }
    ),
    width="stretch",
    hide_index=True,
)
