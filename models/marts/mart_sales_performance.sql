with

orders as (

    select * from {{ ref('orders') }}

),

monthly as (

    select
        date_trunc(date(ordered_at), month) as month,
        count(distinct order_id) as order_count,
        count(distinct customer_id) as customer_count,
        sum(order_total) as revenue,
        sum(order_cost) as total_supply_cost

    from orders
    group by 1

),

final as (

    select
        month,
        order_count,
        customer_count,
        round(revenue, 2) as revenue,
        round(safe_divide(revenue, order_count), 2) as avg_order_value,
        round(total_supply_cost, 2) as total_supply_cost,
        round(safe_divide(revenue - total_supply_cost, revenue), 4) as gross_margin_pct

    from monthly

)

select * from final
order by month
