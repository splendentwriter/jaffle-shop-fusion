#!/usr/bin/env python3
"""
One-off generator for the HR & Payroll domain's raw seed CSVs (Phase 21
of the e-commerce platform build-out): employees, timesheets, payroll
runs, and payroll line items.

Design note: department and job_title are category fields on the
employee, not separate lookup tables - same treatment as "team" on
raw_support_agents. This domain is standalone (company staff, not tied
to warehouses/fulfillment or any other existing domain).

Timesheets only exist for hourly employees (salaried employees don't
clock in/out). A payroll line item's regular_hours/overtime_hours are
rolled up from that employee's *approved* timesheets for the pay
period - a submitted-but-not-yet-approved or rejected timesheet
doesn't get paid, mirroring how a pending/rejected state elsewhere in
this build doesn't count toward a downstream total. A small number of
timesheets are missing clock_out (forgot to clock out) and are
excluded from the hours rollup entirely rather than guessed at.

Usage:
    python3 scripts/generate_hr_domain_seeds.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

fake = Faker()
random.seed(197)
Faker.seed(197)

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "jaffle-data"

N_EMPLOYEES = 45
N_PAYROLL_PERIODS = 26  # ~1 year of biweekly runs

DEPARTMENTS = [
    "Engineering",
    "Sales",
    "Marketing",
    "Customer Support",
    "Warehouse Operations",
    "Finance",
    "People Ops",
    "Executive",
]
JOB_TITLES = {
    "Engineering": ["Software Engineer", "Senior Software Engineer", "Engineering Manager", "QA Engineer"],
    "Sales": ["Account Executive", "Sales Development Rep", "Sales Manager"],
    "Marketing": ["Marketing Specialist", "Content Marketer", "Marketing Manager"],
    "Customer Support": ["Support Associate", "Support Team Lead"],
    "Warehouse Operations": ["Warehouse Associate", "Picker/Packer", "Warehouse Supervisor"],
    "Finance": ["Accountant", "Financial Analyst", "Finance Manager"],
    "People Ops": ["HR Generalist", "Recruiter", "People Ops Manager"],
    "Executive": ["VP", "Director"],
}
EMPLOYMENT_TYPES = ["full_time", "part_time", "contractor"]
STATUSES = ["active", "on_leave", "terminated"]
TIMESHEET_STATUSES = ["approved", "submitted", "rejected"]


def write_csv(name, fieldnames, rows):
    path = SEEDS_DIR / name
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {path}")


def fmt_dt(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def fmt_date(dt):
    return dt.strftime("%Y-%m-%d")


def build_employees(now):
    employees = []
    for _ in range(N_EMPLOYEES):
        department = random.choice(DEPARTMENTS)
        job_title = random.choice(JOB_TITLES[department])
        employment_type = random.choices(EMPLOYMENT_TYPES, weights=[70, 20, 10])[0]
        pay_type = "salary" if employment_type == "full_time" and random.random() < 0.75 else "hourly"

        hire_date = now - timedelta(days=random.randint(30, 6 * 365))
        status = random.choices(STATUSES, weights=[85, 5, 10])[0]
        termination_date = ""
        if status == "terminated":
            termination_date = fmt_date(hire_date + timedelta(days=random.randint(60, (now - hire_date).days)))

        hourly_rate_cents = ""
        annual_salary_cents = ""
        if pay_type == "hourly":
            hourly_rate_cents = random.randint(1800, 5500)
        else:
            annual_salary_cents = random.randint(55000, 165000) * 100

        employees.append(
            {
                "id": str(uuid.uuid4()),
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": fake.company_email(),
                "department": department,
                "job_title": job_title,
                "employment_type": employment_type,
                "pay_type": pay_type,
                "hourly_rate_cents": hourly_rate_cents,
                "annual_salary_cents": annual_salary_cents,
                "status": status,
                "hire_date": fmt_date(hire_date),
                "termination_date": termination_date,
            }
        )
    return employees


def build_payroll_runs(now):
    runs = []
    period_end = now - timedelta(days=now.weekday())  # most recent Sunday-ish anchor
    for i in range(N_PAYROLL_PERIODS):
        this_end = period_end - timedelta(days=14 * i)
        this_start = this_end - timedelta(days=13)
        pay_date = this_end + timedelta(days=5)
        # the most recent 2 periods haven't finished processing yet
        if i == 0:
            status = "draft"
        elif i == 1:
            status = "processing"
        else:
            status = "paid"
        runs.append(
            {
                "id": str(uuid.uuid4()),
                "pay_period_start": fmt_date(this_start),
                "pay_period_end": fmt_date(this_end),
                "pay_date": fmt_date(pay_date),
                "status": status,
            }
        )
    return runs


def is_active_during(employee, period_start, period_end):
    hire_date = datetime.strptime(employee["hire_date"], "%Y-%m-%d")
    if hire_date > period_end:
        return False
    if employee["termination_date"]:
        term_date = datetime.strptime(employee["termination_date"], "%Y-%m-%d")
        if term_date < period_start:
            return False
    return True


def build_timesheets_and_payroll(employees, runs):
    timesheets = []
    line_items = []

    hourly_employees = [e for e in employees if e["pay_type"] == "hourly"]

    for run in runs:
        if run["status"] == "draft":
            continue  # not processed yet, no line items generated

        period_start = datetime.strptime(run["pay_period_start"], "%Y-%m-%d")
        period_end = datetime.strptime(run["pay_period_end"], "%Y-%m-%d")

        for employee in employees:
            if not is_active_during(employee, period_start, period_end):
                continue

            if employee["pay_type"] == "hourly":
                approved_regular = 0.0
                approved_overtime = 0.0

                day = period_start
                while day <= period_end:
                    if day.weekday() < 5 and random.random() < 0.94:  # weekday, usually worked
                        clock_in_hour = random.uniform(7.5, 9.5)
                        clock_in = day + timedelta(hours=clock_in_hour)
                        shift_hours = round(
                            random.choices(
                                [random.uniform(6, 8), random.uniform(8, 8.5), random.uniform(9, 11)],
                                weights=[15, 70, 15],
                            )[0],
                            2,
                        )

                        ts_status = random.choices(TIMESHEET_STATUSES, weights=[85, 10, 5])[0]
                        missing_clock_out = random.random() < 0.02

                        clock_out = "" if missing_clock_out else fmt_dt(clock_in + timedelta(hours=shift_hours))
                        hours_worked = "" if missing_clock_out else shift_hours

                        timesheets.append(
                            {
                                "id": str(uuid.uuid4()),
                                "employee_id": employee["id"],
                                "work_date": fmt_date(day),
                                "clock_in": fmt_dt(clock_in),
                                "clock_out": clock_out,
                                "hours_worked": hours_worked,
                                "status": ts_status,
                            }
                        )

                        if ts_status == "approved" and not missing_clock_out:
                            regular = min(shift_hours, 8)
                            overtime = max(shift_hours - 8, 0)
                            approved_regular += regular
                            approved_overtime += overtime
                    day += timedelta(days=1)

                regular_hours = round(approved_regular, 2)
                overtime_hours = round(approved_overtime, 2)
                gross_pay_cents = round(regular_hours * employee["hourly_rate_cents"] + overtime_hours * employee["hourly_rate_cents"] * 1.5)
            else:
                regular_hours = 80.0
                overtime_hours = 0.0
                gross_pay_cents = round(employee["annual_salary_cents"] / 26)

            federal_tax_cents = round(gross_pay_cents * 0.12)
            state_tax_cents = round(gross_pay_cents * 0.04)
            other_deductions_cents = round(gross_pay_cents * random.uniform(0.03, 0.08))
            net_pay_cents = gross_pay_cents - federal_tax_cents - state_tax_cents - other_deductions_cents

            line_items.append(
                {
                    "id": str(uuid.uuid4()),
                    "payroll_run_id": run["id"],
                    "employee_id": employee["id"],
                    "regular_hours": regular_hours,
                    "overtime_hours": overtime_hours,
                    "gross_pay_cents": gross_pay_cents,
                    "federal_tax_cents": federal_tax_cents,
                    "state_tax_cents": state_tax_cents,
                    "other_deductions_cents": other_deductions_cents,
                    "net_pay_cents": net_pay_cents,
                }
            )

    return timesheets, line_items


def main():
    now = datetime.now()
    print(f"generating HR/payroll-domain seeds: {N_EMPLOYEES} employees, {N_PAYROLL_PERIODS} payroll periods")

    employees = build_employees(now)
    runs = build_payroll_runs(now)
    timesheets, line_items = build_timesheets_and_payroll(employees, runs)

    write_csv(
        "raw_employees.csv",
        [
            "id", "first_name", "last_name", "email", "department", "job_title",
            "employment_type", "pay_type", "hourly_rate_cents", "annual_salary_cents",
            "status", "hire_date", "termination_date",
        ],
        employees,
    )
    write_csv(
        "raw_timesheets.csv",
        ["id", "employee_id", "work_date", "clock_in", "clock_out", "hours_worked", "status"],
        timesheets,
    )
    write_csv(
        "raw_payroll_runs.csv",
        ["id", "pay_period_start", "pay_period_end", "pay_date", "status"],
        runs,
    )
    write_csv(
        "raw_payroll_line_items.csv",
        [
            "id", "payroll_run_id", "employee_id", "regular_hours", "overtime_hours",
            "gross_pay_cents", "federal_tax_cents", "state_tax_cents",
            "other_deductions_cents", "net_pay_cents",
        ],
        line_items,
    )


if __name__ == "__main__":
    main()
