with

-- exclude the current, still-in-progress calendar month so the "latest
-- month" comparison is always a complete month against a complete prior
-- month, not a partial month that would look artificially low
sales as (

    select * from {{ ref('mart_sales_performance') }}
    where month < date_trunc(current_date(), month)

),

ranked_sales as (

    select
        *,
        row_number() over (order by month desc) as recency_rank

    from sales

),

current_month as (

    select * from ranked_sales where recency_rank = 1

),

prior_month as (

    select * from ranked_sales where recency_rank = 2

),

checkout_funnel as (

    select
        count(*) as checkouts_started,
        countif(status = 'completed') as checkouts_completed

    from {{ ref('fct_checkout') }}

),

payment_summary as (

    select
        sum(captured_amount_cents) as captured_cents,
        sum(refunded_amount_cents) as refunded_cents

    from {{ ref('fct_payment') }}

),

shipping_summary as (

    select
        countif(status = 'delivered') as delivered,
        countif(status = 'delivered' and not was_late) as delivered_on_time

    from {{ ref('fct_shipment') }}

),

inventory_summary as (

    select
        countif(is_below_reorder_point) as low_stock_sku_count

    from {{ ref('fct_inventory_position') }}

),

final as (

    select

        ---------- period
        current_month.month as current_month,

        ---------- revenue
        prior_month.month as prior_month,
        current_month.revenue as net_revenue,
        prior_month.revenue as prior_month_revenue,
        round(safe_divide(current_month.revenue - prior_month.revenue, prior_month.revenue), 4)
            as revenue_change_pct,

        ---------- orders
        current_month.order_count as orders,
        prior_month.order_count as prior_month_orders,
        round(
            safe_divide(current_month.order_count - prior_month.order_count, prior_month.order_count), 4
        ) as orders_change_pct,

        ---------- customers
        current_month.customer_count as customers,
        prior_month.customer_count as prior_month_customers,
        round(
            safe_divide(current_month.customer_count - prior_month.customer_count, prior_month.customer_count),
            4
        ) as customers_change_pct,

        ---------- aov
        current_month.avg_order_value as avg_order_value,
        prior_month.avg_order_value as prior_month_avg_order_value,
        round(
            safe_divide(
                current_month.avg_order_value - prior_month.avg_order_value, prior_month.avg_order_value
            ), 4
        ) as avg_order_value_change_pct,

        ---------- margin
        current_month.gross_margin_pct as gross_margin_pct,

        ---------- funnel-wide health rates (not month-scoped: the checkout/
        ---------- payment/shipment funnel is a much smaller, separate dataset
        ---------- from the order history above - see CONVENTIONS.md)
        round(safe_divide(checkout_funnel.checkouts_completed, checkout_funnel.checkouts_started), 4)
            as checkout_conversion_rate,
        round(safe_divide(payment_summary.refunded_cents, payment_summary.captured_cents), 4) as refund_rate,
        round(safe_divide(shipping_summary.delivered_on_time, shipping_summary.delivered), 4)
            as on_time_delivery_rate,
        inventory_summary.low_stock_sku_count

    from current_month
    cross join prior_month
    cross join checkout_funnel
    cross join payment_summary
    cross join shipping_summary
    cross join inventory_summary

)

select * from final
