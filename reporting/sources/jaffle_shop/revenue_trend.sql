select
    date_trunc(date(ordered_at), month) as month,
    round(sum(order_total), 2) as revenue,
    count(distinct order_id) as orders
from `jaffle-shop-505616.jaffle_shop_analytics.orders`
group by 1
order by 1
