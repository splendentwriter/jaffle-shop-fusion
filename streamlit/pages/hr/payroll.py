"""Payroll — headcount, pay trend, and department breakdown."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from components.section_header import section_header
from queries.hr import get_payroll
from utils.formatting import fmt_num, fmt_usd

section_header("HR & Payroll", "Payroll", "🧑‍💼")

payroll = get_payroll()
for col in ["gross_pay", "net_pay"]:
    payroll[col] = payroll[col].astype(float)

kpi_row(
    [
        {"label": "Employees Paid", "value": fmt_num(payroll["employee_id"].nunique())},
        {"label": "Gross Pay", "value": fmt_usd(payroll["gross_pay"].sum())},
        {"label": "Net Pay", "value": fmt_usd(payroll["net_pay"].sum())},
        {"label": "Hours Mismatches", "value": fmt_num(payroll["has_regular_hours_mismatch"].sum())},
    ]
)

st.subheader("Net pay by period")
trend = payroll.groupby("pay_date", as_index=False)["net_pay"].sum().sort_values("pay_date")
fig = px.line(trend, x="pay_date", y="net_pay", markers=True)
fig.update_layout(yaxis_title="Net Pay ($)", xaxis_title=None, height=380)
fig.update_yaxes(tickprefix="$", separatethousands=True)
st.plotly_chart(fig, width="stretch")

departments = sorted(payroll["department"].dropna().unique())
selected_department = st.selectbox("Department", ["All"] + departments)
filtered = payroll if selected_department == "All" else payroll[payroll["department"] == selected_department]

col1, col2 = st.columns(2)
with col1:
    st.subheader("Gross pay by department")
    by_department = filtered.groupby("department", as_index=False)["gross_pay"].sum()
    fig = px.bar(by_department, x="gross_pay", y="department", orientation="h")
    fig.update_layout(yaxis_title=None, xaxis_title="Gross Pay ($)", height=380)
    fig.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig, width="stretch")

with col2:
    st.subheader("Pay type mix")
    pay_type_counts = filtered["pay_type"].value_counts().reset_index()
    pay_type_counts.columns = ["Pay Type", "Count"]
    fig = px.pie(pay_type_counts, names="Pay Type", values="Count", hole=0.4)
    fig.update_layout(height=380)
    st.plotly_chart(fig, width="stretch")

st.subheader("Hours mismatches")
mismatches = filtered[filtered["has_regular_hours_mismatch"]]
if mismatches.empty:
    st.success("No hourly employees with a paid-vs-timesheet hours mismatch.")
else:
    st.dataframe(
        mismatches[
            [
                "employee_name", "department", "pay_period_start", "pay_period_end",
                "regular_hours", "timesheet_regular_hours", "overtime_hours", "timesheet_overtime_hours",
            ]
        ].rename(
            columns={
                "employee_name": "Employee",
                "department": "Department",
                "pay_period_start": "Period Start",
                "pay_period_end": "Period End",
                "regular_hours": "Paid Regular Hrs",
                "timesheet_regular_hours": "Timesheet Regular Hrs",
                "overtime_hours": "Paid OT Hrs",
                "timesheet_overtime_hours": "Timesheet OT Hrs",
            }
        ),
        width="stretch",
        hide_index=True,
    )
