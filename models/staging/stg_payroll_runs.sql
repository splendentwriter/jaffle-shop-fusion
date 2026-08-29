with

source as (

    select * from {{ source('ecom', 'raw_payroll_runs') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as payroll_run_id,

        ---------- text
        status,

        ---------- timestamps
        pay_period_start,
        pay_period_end,
        pay_date

    from source

)

select * from renamed
