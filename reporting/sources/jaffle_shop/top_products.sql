select
    product_name,
    count(distinct order_id) as orders,
    round(sum(product_price), 2) as revenue
from `jaffle-shop-505616.jaffle_shop_analytics.order_items`
group by 1
order by revenue desc
limit 10
