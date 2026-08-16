select
    count(distinct order_id) as total_orders,
    count(distinct customer_id) as total_customers,
    round(sum(order_total), 2) as total_revenue,
    round(avg(order_total), 2) as avg_order_value
from `jaffle-shop-505616.jaffle_shop_analytics.orders`
