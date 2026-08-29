with

employees as (

    select * from {{ ref('stg_employees') }}

),

final as (

    select

        ----------  ids
        employee_id,

        ---------- text
        first_name,
        last_name,
        first_name || ' ' || last_name as full_name,
        email,
        department,
        job_title,
        employment_type,
        pay_type,
        status,

        ---------- numerics
        hourly_rate,
        annual_salary,

        ---------- timestamps
        hire_date,
        termination_date,
        date_diff(coalesce(termination_date, current_date()), hire_date, day) as tenure_days,

        ---------- booleans
        status = 'active' as is_active

    from employees

)

select * from final
