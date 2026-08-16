select
    count(*) as checkouts_started,
    countif(status = 'completed') as checkouts_completed,
    countif(status = 'failed') as checkouts_failed,
    countif(status = 'abandoned') as checkouts_abandoned
from `jaffle-shop-505616.jaffle_shop_analytics.fct_checkout`
