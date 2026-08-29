with

source as (

    select * from {{ source('ecom', 'raw_timesheets') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as timesheet_id,
        employee_id,

        ---------- text
        status,

        ---------- numerics
        hours_worked,

        ---------- timestamps
        work_date,
        clock_in,
        clock_out

    from source

)

select * from renamed
