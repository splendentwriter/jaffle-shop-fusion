"""Pipeline Health — dbt build run history: success rate and duration trend."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from components.section_header import section_header
from queries.data_platform import get_pipeline_health
from utils.formatting import fmt_num, fmt_pct

section_header("Data Platform", "Pipeline Health", "⚙️")

runs = get_pipeline_health()

kpi_row(
    [
        {"label": "Runs", "value": fmt_num(len(runs))},
        {"label": "Success Rate", "value": fmt_pct(runs["is_successful"].mean())},
        {"label": "Avg Duration (s)", "value": fmt_num(runs["total_execution_time_seconds"].mean())},
        {"label": "Failed Runs", "value": fmt_num((~runs["is_successful"]).sum())},
    ]
)

st.subheader("Run duration over time")
fig = px.line(
    runs.sort_values("started_at"),
    x="started_at",
    y="total_execution_time_seconds",
    color="is_successful",
    markers=True,
    labels={"started_at": "Run Time", "total_execution_time_seconds": "Duration (s)", "is_successful": "Successful"},
)
st.plotly_chart(fig, width="stretch")

st.subheader("Recent runs")
st.dataframe(
    runs[
        ["invocation_id", "command", "target_name", "started_at", "model_success_count", "model_error_count", "test_pass_count", "test_fail_count", "total_execution_time_seconds", "is_successful"]
    ].rename(
        columns={
            "invocation_id": "Invocation",
            "command": "Command",
            "target_name": "Target",
            "started_at": "Started",
            "model_success_count": "Models OK",
            "model_error_count": "Models Failed",
            "test_pass_count": "Tests Passed",
            "test_fail_count": "Tests Failed",
            "total_execution_time_seconds": "Duration (s)",
            "is_successful": "Successful",
        }
    ),
    width="stretch",
    hide_index=True,
)
