"""Employees — headcount by department, tenure, and recent departures."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from components.section_header import section_header
from queries.hr import get_employees
from utils.formatting import fmt_num

section_header("HR & Payroll", "Employees", "👤")

employees = get_employees()
employees["tenure_years"] = (employees["tenure_days"] / 365).round(1)
active = employees[employees["status"] == "active"]
terminated = employees[employees["status"] == "terminated"]

kpi_row(
    [
        {"label": "Total Employees", "value": fmt_num(len(employees))},
        {"label": "Active", "value": fmt_num(len(active))},
        {"label": "On Leave", "value": fmt_num((employees["status"] == "on_leave").sum())},
        {"label": "Terminated", "value": fmt_num(len(terminated))},
    ]
)

st.subheader("Employees by department")
by_department = active.groupby("department", as_index=False).size().rename(columns={"size": "employees"})
fig = px.bar(by_department, x="employees", y="department", orientation="h")
fig.update_layout(yaxis_title=None, xaxis_title="Employees", height=380)
fig.update_yaxes(categoryorder="total ascending")
st.plotly_chart(fig, width="stretch")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Longest-serving employees")
    st.caption("Active employees, ranked by tenure.")
    longest_serving = active.sort_values("tenure_years", ascending=False).head(10)
    st.dataframe(
        longest_serving[["full_name", "department", "job_title", "hire_date", "tenure_years"]].rename(
            columns={
                "full_name": "Employee",
                "department": "Department",
                "job_title": "Job Title",
                "hire_date": "Hire Date",
                "tenure_years": "Tenure (yrs)",
            }
        ),
        width="stretch",
        hide_index=True,
    )

with col2:
    st.subheader("Recent departures")
    st.caption(
        "Most recently terminated employees. The data only tracks terminations that "
        "already happened — there's no notice-period field to forecast who's leaving next."
    )
    if terminated.empty:
        st.success("No terminated employees on record.")
    else:
        recent_departures = terminated.sort_values("termination_date", ascending=False).head(10)
        st.dataframe(
            recent_departures[
                ["full_name", "department", "job_title", "termination_date", "tenure_years"]
            ].rename(
                columns={
                    "full_name": "Employee",
                    "department": "Department",
                    "job_title": "Job Title",
                    "termination_date": "Termination Date",
                    "tenure_years": "Tenure (yrs)",
                }
            ),
            width="stretch",
            hide_index=True,
        )
