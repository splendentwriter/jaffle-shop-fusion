"""Data Quality — current test pass/fail state across the jaffle_shop project."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from components.section_header import section_header
from queries.data_platform import get_data_quality
from utils.formatting import fmt_num, fmt_pct

section_header("Data Platform", "Data Quality", "🔍")

tests = get_data_quality()

kpi_row(
    [
        {"label": "Tests", "value": fmt_num(len(tests))},
        {"label": "Passing", "value": fmt_pct((tests["status"] == "pass").mean())},
        {"label": "Failing", "value": fmt_num(tests["is_failing"].sum())},
        {"label": "Warning", "value": fmt_num(tests["is_warning"].sum())},
    ]
)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Status breakdown")
    status_counts = tests["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    fig = px.pie(status_counts, names="Status", values="Count", hole=0.4)
    st.plotly_chart(fig, width="stretch")

with col2:
    st.subheader("Tests by type")
    type_counts = tests["test_type"].value_counts().reset_index()
    type_counts.columns = ["Test Type", "Count"]
    fig = px.bar(type_counts, x="Test Type", y="Count")
    st.plotly_chart(fig, width="stretch")

st.subheader("Failing and warning tests")
issues = tests[tests["is_failing"] | tests["is_warning"]].sort_values("is_failing", ascending=False)
if issues.empty:
    st.success("No failing or warning tests.")
else:
    st.dataframe(
        issues[
            ["table_name", "column_name", "test_name", "test_type", "status", "severity", "failures", "last_run_at"]
        ].rename(
            columns={
                "table_name": "Table",
                "column_name": "Column",
                "test_name": "Test",
                "test_type": "Type",
                "status": "Status",
                "severity": "Severity",
                "failures": "Failures",
                "last_run_at": "Last Run",
            }
        ),
        width="stretch",
        hide_index=True,
    )
