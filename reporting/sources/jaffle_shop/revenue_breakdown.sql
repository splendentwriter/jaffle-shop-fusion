select
    round(sum(gross_revenue_cents) / 100.0, 2) as gross_revenue,
    round(sum(net_revenue_cents) / 100.0, 2) as net_revenue,
    round(sum(discount_amount_cents) / 100.0, 2) as total_discounts,
    round(sum(processing_fee_cents) / 100.0, 2) as total_processing_fees,
    round(sum(refunded_amount_cents) / 100.0, 2) as total_refunds
from `jaffle-shop-505616.jaffle_shop_analytics.fct_revenue`
