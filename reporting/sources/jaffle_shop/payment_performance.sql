select
    count(*) as payment_attempts,
    countif(attempt_status = 'captured') as captured,
    countif(attempt_status = 'declined') as declined,
    countif(attempt_status = 'error') as errored,
    round(sum(captured_amount_cents) / 100.0, 2) as total_captured,
    round(sum(refunded_amount_cents) / 100.0, 2) as total_refunded
from `jaffle-shop-505616.jaffle_shop_analytics.fct_payment`
