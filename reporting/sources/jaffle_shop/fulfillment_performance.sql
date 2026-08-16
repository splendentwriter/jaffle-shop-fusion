select
    count(*) as fulfillment_orders,
    countif(is_shipped) as shipped,
    countif(is_cancelled) as cancelled,
    round(avg(hours_to_ship), 1) as avg_hours_to_ship
from `jaffle-shop-505616.jaffle_shop_analytics.fct_fulfillment_order`
