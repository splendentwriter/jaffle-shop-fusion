with

orders as (

    select * from {{ ref('orders') }}

),

customer_cohort as (

    select
        customer_id,
        date_trunc(date(min(ordered_at)), month) as cohort_month

    from orders
    group by 1

),

order_months as (

    select distinct
        customer_id,
        date_trunc(date(ordered_at), month) as order_month

    from orders

),

cohort_activity as (

    select
        customer_cohort.cohort_month,
        date_diff(order_months.order_month, customer_cohort.cohort_month, month) as month_index,
        order_months.customer_id

    from order_months
    inner join customer_cohort on order_months.customer_id = customer_cohort.customer_id

),

cohort_sizes as (

    select
        cohort_month,
        count(distinct customer_id) as cohort_size

    from customer_cohort
    group by 1

),

final as (

    select
        cohort_activity.cohort_month,
        cohort_activity.month_index,
        count(distinct cohort_activity.customer_id) as retained_customers,
        cohort_sizes.cohort_size,
        round(
            safe_divide(count(distinct cohort_activity.customer_id), cohort_sizes.cohort_size), 4
        ) as retention_rate

    from cohort_activity
    inner join cohort_sizes on cohort_activity.cohort_month = cohort_sizes.cohort_month
    group by 1, 2, 4

)

select * from final
order by cohort_month, month_index
