select
    count(*) as shipments,
    countif(status = 'delivered') as delivered,
    countif(was_late) as late_deliveries,
    round(avg(hours_to_deliver), 1) as avg_hours_to_deliver,
    round(
        100.0 * countif(status = 'delivered' and not was_late) / nullif(countif(status = 'delivered'), 0), 1
    ) as on_time_delivery_pct
from `jaffle-shop-505616.jaffle_shop_analytics.fct_shipment`
