with

payroll as (

    select * from {{ ref('fct_payroll_line_item') }}

),

employees as (

    select * from {{ ref('dim_employee') }}

),

final as (

    select

        ----------  ids
        payroll.payroll_line_item_id,
        payroll.payroll_run_id,
        payroll.employee_id,

        ---------- text
        employees.full_name as employee_name,
        employees.department,
        employees.job_title,
        employees.pay_type,
        payroll.payroll_run_status,

        ---------- numerics
        payroll.regular_hours,
        payroll.overtime_hours,
        payroll.timesheet_regular_hours,
        payroll.timesheet_overtime_hours,
        payroll.gross_pay,
        payroll.federal_tax_cents,
        payroll.state_tax_cents,
        payroll.other_deductions_cents,
        payroll.net_pay,

        ---------- timestamps
        payroll.pay_period_start,
        payroll.pay_period_end,
        payroll.pay_date,

        ---------- booleans
        employees.pay_type = 'hourly'
            and payroll.regular_hours != coalesce(payroll.timesheet_regular_hours, 0)
            as has_regular_hours_mismatch

    from payroll
    left join employees on payroll.employee_id = employees.employee_id

)

select * from final
