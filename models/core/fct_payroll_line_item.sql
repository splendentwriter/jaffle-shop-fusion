with

payroll_runs as (

    select * from {{ ref('stg_payroll_runs') }}

),

line_items as (

    select * from {{ ref('stg_payroll_line_items') }}

),

timesheets as (

    select * from {{ ref('stg_timesheets') }}

),

approved_timesheet_hours as (

    select
        timesheets.employee_id,
        payroll_runs.payroll_run_id,
        sum(least(timesheets.hours_worked, 8)) as timesheet_regular_hours,
        sum(greatest(timesheets.hours_worked - 8, 0)) as timesheet_overtime_hours

    from timesheets
    inner join payroll_runs
        on timesheets.work_date between payroll_runs.pay_period_start and payroll_runs.pay_period_end
    where timesheets.status = 'approved'
      and timesheets.hours_worked is not null
    group by 1, 2

),

final as (

    select

        ----------  ids
        line_items.payroll_line_item_id,
        line_items.payroll_run_id,
        line_items.employee_id,

        ---------- text
        payroll_runs.status as payroll_run_status,

        ---------- numerics
        line_items.regular_hours,
        line_items.overtime_hours,
        approved_timesheet_hours.timesheet_regular_hours,
        approved_timesheet_hours.timesheet_overtime_hours,
        line_items.gross_pay_cents,
        line_items.gross_pay,
        line_items.federal_tax_cents,
        line_items.state_tax_cents,
        line_items.other_deductions_cents,
        line_items.net_pay_cents,
        line_items.net_pay,

        ---------- timestamps
        payroll_runs.pay_period_start,
        payroll_runs.pay_period_end,
        payroll_runs.pay_date

    from line_items
    inner join payroll_runs on line_items.payroll_run_id = payroll_runs.payroll_run_id
    left join approved_timesheet_hours
        on line_items.employee_id = approved_timesheet_hours.employee_id
        and line_items.payroll_run_id = approved_timesheet_hours.payroll_run_id

)

select * from final
