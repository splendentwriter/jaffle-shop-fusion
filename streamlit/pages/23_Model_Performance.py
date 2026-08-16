"""Model Performance — per-model build duration and reliability."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from queries.data_platform import get_model_performance
from utils.config import APP_ICON, APP_TITLE
from utils.formatting import fmt_num, fmt_pct

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

st.title("🏗️ Model Performance")

executions = get_model_performance()

kpi_row(
    [
        {"label": "Model Executions", "value": fmt_num(len(executions))},
        {"label": "Distinct Models", "value": fmt_num(executions["unique_id"].nunique())},
        {"label": "Success Rate", "value": fmt_pct(executions["is_successful"].mean())},
        {"label": "Avg Duration (s)", "value": fmt_num(executions["execution_time_seconds"].mean())},
    ]
)

by_model = (
    executions.groupby("name")
    .agg(
        executions=("model_execution_id", "count"),
        avg_duration=("execution_time_seconds", "mean"),
        max_duration=("execution_time_seconds", "max"),
        error_count=("is_error", "sum"),
    )
    .reset_index()
    .sort_values("avg_duration", ascending=False)
)

st.subheader("Slowest models (avg build duration)")
top20 = by_model.head(20)
fig = px.bar(top20, x="name", y="avg_duration", labels={"name": "Model", "avg_duration": "Avg Duration (s)"})
st.plotly_chart(fig, width="stretch")

st.subheader("Model summary")
st.dataframe(
    by_model.rename(
        columns={
            "name": "Model",
            "executions": "Executions",
            "avg_duration": "Avg Duration (s)",
            "max_duration": "Max Duration (s)",
            "error_count": "Errors",
        }
    ),
    width="stretch",
    hide_index=True,
)

st.subheader("Models with errors")
errored = by_model[by_model["error_count"] > 0]
if errored.empty:
    st.success("No model build errors recorded.")
else:
    st.dataframe(
        errored.rename(columns={"name": "Model", "error_count": "Errors"})[["Model", "Errors"]],
        width="stretch",
        hide_index=True,
    )
