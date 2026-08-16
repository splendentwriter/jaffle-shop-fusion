with

revenue as (

    select * from {{ ref('fct_revenue') }}

),

checkouts as (

    select checkout_id, completed_at from {{ ref('fct_checkout') }}

),

monthly as (

    select
        date_trunc(date(checkouts.completed_at), month) as month,
        count(distinct revenue.checkout_id) as checkout_count,
        sum(revenue.items_subtotal_cents) as items_subtotal_cents,
        sum(revenue.discount_amount_cents) as discount_amount_cents,
        sum(revenue.refunded_amount_cents) as refunded_amount_cents,
        sum(revenue.processing_fee_cents) as processing_fee_cents,
        sum(revenue.gross_revenue_cents) as gross_revenue_cents,
        sum(revenue.net_revenue_cents) as net_revenue_cents

    from revenue
    inner join checkouts on revenue.checkout_id = checkouts.checkout_id
    group by 1

),

final as (

    select
        month,
        checkout_count,
        round(items_subtotal_cents / 100.0, 2) as items_subtotal,
        round(discount_amount_cents / 100.0, 2) as discount_amount,
        round(refunded_amount_cents / 100.0, 2) as refunded_amount,
        round(processing_fee_cents / 100.0, 2) as processing_fee,
        round(gross_revenue_cents / 100.0, 2) as gross_revenue,
        round(net_revenue_cents / 100.0, 2) as net_revenue,
        round(safe_divide(net_revenue_cents, gross_revenue_cents), 4) as net_margin_pct

    from monthly

)

select * from final
order by month
