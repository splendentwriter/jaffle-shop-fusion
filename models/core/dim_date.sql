with

spine as (

    select * from {{ ref('metricflow_time_spine') }}

),

final as (

    select

        ----------  ids
        {{ dbt_utils.generate_surrogate_key(['date_day']) }} as date_id,

        ---------- dates
        date_day,

        ---------- calendar attributes
        extract(year from date_day) as year_number,
        extract(quarter from date_day) as quarter_number,
        extract(month from date_day) as month_number,
        format_date('%B', date_day) as month_name,
        extract(week from date_day) as week_number,
        extract(dayofweek from date_day) as day_of_week_number,
        format_date('%A', date_day) as day_name,
        extract(dayofweek from date_day) in (1, 7) as is_weekend

    from spine

)

select * from final
