with

source as (

    select * from {{ source('ecom', 'raw_employees') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as employee_id,

        ---------- text
        first_name,
        last_name,
        email,
        department,
        job_title,
        employment_type,
        pay_type,
        status,

        ---------- numerics
        hourly_rate_cents,
        {{ cents_to_dollars('hourly_rate_cents') }} as hourly_rate,
        annual_salary_cents,
        {{ cents_to_dollars('annual_salary_cents') }} as annual_salary,

        ---------- timestamps
        hire_date,
        termination_date

    from source

)

select * from renamed
