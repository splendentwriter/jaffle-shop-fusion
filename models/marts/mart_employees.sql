with

employees as (

    select * from {{ ref('dim_employee') }}

),

final as (

    select

        ----------  ids
        employee_id,

        ---------- text
        full_name,
        email,
        department,
        job_title,
        employment_type,
        pay_type,
        status,

        ---------- numerics
        hourly_rate,
        annual_salary,
        tenure_days,

        ---------- timestamps
        hire_date,
        termination_date,

        ---------- booleans
        is_active

    from employees

)

select * from final
