with

order_items as (

    select * from {{ ref('order_items') }}

),

sales as (

    select
        product_id,
        any_value(product_name) as product_name,
        count(distinct order_id) as order_count,
        count(*) as units_sold,
        round(sum(product_price), 2) as revenue,
        round(sum(supply_cost), 2) as total_supply_cost,
        round(safe_divide(sum(product_price) - sum(supply_cost), sum(product_price)), 4) as margin_pct

    from order_items
    group by 1

),

ratings as (

    select * from {{ ref('dim_product_rating') }}

),

final as (

    select
        sales.product_id,
        sales.product_name,
        sales.order_count,
        sales.units_sold,
        sales.revenue,
        sales.total_supply_cost,
        sales.margin_pct,
        ratings.average_rating,
        ratings.published_review_count

    from sales
    left join ratings on sales.product_id = ratings.product_id

)

select * from final
order by revenue desc
