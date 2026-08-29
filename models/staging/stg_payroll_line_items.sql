with

source as (

    select * from {{ source('ecom', 'raw_payroll_line_items') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as payroll_line_item_id,
        payroll_run_id,
        employee_id,

        ---------- numerics
        regular_hours,
        overtime_hours,
        gross_pay_cents,
        {{ cents_to_dollars('gross_pay_cents') }} as gross_pay,
        federal_tax_cents,
        state_tax_cents,
        other_deductions_cents,
        net_pay_cents,
        {{ cents_to_dollars('net_pay_cents') }} as net_pay

    from source

)

select * from renamed
