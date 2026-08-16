with

orders as (

    select * from {{ ref('orders') }}

),

categorized as (

    select
        case
            when is_food_order and is_drink_order then 'food_and_drink'
            when is_food_order then 'food_only'
            when is_drink_order then 'drink_only'
            else 'other'
        end as category,
        order_id,
        order_total

    from orders

),

final as (

    select
        category,
        count(distinct order_id) as order_count,
        round(sum(order_total), 2) as revenue

    from categorized
    group by 1

)

select * from final
order by revenue desc
