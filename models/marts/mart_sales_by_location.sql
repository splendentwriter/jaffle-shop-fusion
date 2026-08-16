with

orders as (

    select * from {{ ref('orders') }}

),

locations as (

    select * from {{ ref('locations') }}

),

final as (

    select
        locations.location_id,
        locations.location_name,
        count(distinct orders.order_id) as order_count,
        round(sum(orders.order_total), 2) as revenue,
        round(safe_divide(sum(orders.order_total), count(distinct orders.order_id)), 2) as avg_order_value

    from orders
    left join locations on orders.location_id = locations.location_id
    group by 1, 2

)

select * from final
order by revenue desc
