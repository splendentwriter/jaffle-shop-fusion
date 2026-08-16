with

checkouts as (

    select * from {{ ref('stg_checkouts') }}

),

items as (

    select * from {{ ref('stg_checkout_items') }}

),

item_summary as (

    select
        checkout_id,
        count(*) as line_item_count,
        sum(quantity) as total_quantity,
        sum(quantity * unit_price_cents) as items_subtotal_cents

    from items
    group by checkout_id

),

events as (

    select * from {{ ref('stg_checkout_events') }}

),

funnel as (

    select
        checkout_id,
        min(case when event_type = 'address_entered' then occurred_at end) as address_entered_at,
        min(case when event_type = 'shipping_selected' then occurred_at end) as shipping_selected_at

    from events
    group by checkout_id

),

failures as (

    select
        checkout_id,
        count(*) as failure_count,
        -- arbitrary but deterministic pick when a checkout has more than one failure
        max(failure_reason) as last_failure_reason

    from {{ ref('stg_checkout_failures') }}
    group by checkout_id

),

final as (

    select

        ----------  ids
        checkouts.checkout_id,
        checkouts.cart_id,
        checkouts.customer_id,

        ---------- text
        checkouts.status,
        checkouts.shipping_method,
        failures.last_failure_reason,

        ---------- numerics
        coalesce(item_summary.line_item_count, 0) as line_item_count,
        coalesce(item_summary.total_quantity, 0) as total_quantity,
        coalesce(item_summary.items_subtotal_cents, 0) as items_subtotal_cents,
        checkouts.shipping_cost_cents,
        coalesce(item_summary.items_subtotal_cents, 0) + checkouts.shipping_cost_cents as order_total_cents,
        coalesce(failures.failure_count, 0) as failure_count,

        ---------- timestamps
        checkouts.started_at,
        funnel.address_entered_at,
        funnel.shipping_selected_at,
        checkouts.completed_at,
        timestamp_diff(checkouts.completed_at, checkouts.started_at, second) as time_to_complete_seconds,

        ---------- booleans
        checkouts.status = 'completed' as is_completed

    from checkouts
    left join item_summary on checkouts.checkout_id = item_summary.checkout_id
    left join funnel on checkouts.checkout_id = funnel.checkout_id
    left join failures on checkouts.checkout_id = failures.checkout_id

)

select * from final
