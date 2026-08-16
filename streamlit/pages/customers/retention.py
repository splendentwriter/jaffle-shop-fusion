"""Retention & Cohorts — monthly cohort retention heatmap."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from components.section_header import section_header
from queries.customers import get_retention_cohorts
from utils.formatting import fmt_pct

section_header("Customers", "Customer Retention", "🔁")

cohorts = get_retention_cohorts()
cohorts["cohort_month"] = cohorts["cohort_month"].astype(str)

st.info(
    "There's a real ~1-year gap in the underlying order history (see the Executive Overview page). "
    "Cohorts whose first order falls before the gap will show retention only at month 0 and then a "
    "sparse jump wherever a customer happened to reorder after the gap — an accurate reflection of the "
    "data, not a bug.",
    icon="ℹ️",
)

month0 = cohorts[cohorts["month_index"] == 0]
retention_30 = cohorts[cohorts["month_index"] == 1]["retention_rate"].mean()
retention_90 = cohorts[cohorts["month_index"] == 3]["retention_rate"].mean()

kpi_row(
    [
        {"label": "Cohorts", "value": str(month0["cohort_month"].nunique())},
        {"label": "Total Cohort Customers", "value": f"{int(month0['cohort_size'].sum()):,}"},
        {"label": "Avg Month-1 Retention", "value": fmt_pct(retention_30) if retention_30 == retention_30 else "—"},
        {"label": "Avg Month-3 Retention", "value": fmt_pct(retention_90) if retention_90 == retention_90 else "—"},
    ]
)

st.subheader("Retention heatmap")
pivot = cohorts.pivot(index="cohort_month", columns="month_index", values="retention_rate")
fig = px.imshow(
    pivot,
    labels=dict(x="Months Since First Order", y="Cohort", color="Retention"),
    color_continuous_scale="Blues",
    aspect="auto",
    text_auto=".0%",
)
fig.update_layout(height=max(400, 30 * len(pivot)))
st.plotly_chart(fig, width="stretch")

with st.expander("Underlying data"):
    st.dataframe(cohorts, width="stretch", hide_index=True)
