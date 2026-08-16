with

fulfillment_orders as (

    select * from {{ ref('stg_fulfillment_orders') }}

),

items as (

    select * from {{ ref('stg_fulfillment_items') }}

),

item_summary as (

    select
        fulfillment_order_id,
        count(*) as line_item_count,
        sum(quantity) as total_quantity

    from items
    group by 1

),

events as (

    select * from {{ ref('stg_fulfillment_events') }}

),

funnel as (

    select
        fulfillment_order_id,
        min(case when event_type = 'picking_started' then occurred_at end) as picking_started_at,
        min(case when event_type = 'picking_completed' then occurred_at end) as picking_completed_at,
        min(case when event_type = 'packing_started' then occurred_at end) as packing_started_at,
        min(case when event_type = 'packing_completed' then occurred_at end) as packing_completed_at,
        min(case when event_type = 'shipped' then occurred_at end) as shipped_event_at

    from events
    group by 1

),

final as (

    select

        ----------  ids
        fulfillment_orders.fulfillment_order_id,
        fulfillment_orders.checkout_id,
        fulfillment_orders.warehouse_id,

        ---------- text
        fulfillment_orders.status,

        ---------- numerics
        coalesce(item_summary.line_item_count, 0) as line_item_count,
        coalesce(item_summary.total_quantity, 0) as total_quantity,

        ---------- timestamps
        fulfillment_orders.created_at,
        funnel.picking_started_at,
        funnel.picking_completed_at,
        funnel.packing_started_at,
        funnel.packing_completed_at,
        fulfillment_orders.completed_at as shipped_at,
        timestamp_diff(fulfillment_orders.completed_at, fulfillment_orders.created_at, hour)
            as hours_to_ship,

        ---------- booleans
        fulfillment_orders.status = 'shipped' as is_shipped,
        fulfillment_orders.status = 'cancelled' as is_cancelled

    from fulfillment_orders
    left join item_summary on fulfillment_orders.fulfillment_order_id = item_summary.fulfillment_order_id
    left join funnel on fulfillment_orders.fulfillment_order_id = funnel.fulfillment_order_id

)

select * from final
