with

shipments as (

    select * from {{ ref('stg_shipments') }}

),

items as (

    select * from {{ ref('stg_shipment_items') }}

),

item_summary as (

    select
        shipment_id,
        count(*) as line_item_count,
        sum(quantity) as total_quantity

    from items
    group by 1

),

tracking as (

    select * from {{ ref('stg_tracking_events') }}

),

delivered_event as (

    select
        shipment_id,
        min(occurred_at) as delivered_at

    from tracking
    where event_type = 'delivered'
    group by 1

),

attempts as (

    select
        shipment_id,
        count(*) as delivery_attempt_count

    from {{ ref('stg_delivery_attempts') }}
    group by 1

),

final as (

    select

        ----------  ids
        shipments.shipment_id,
        shipments.fulfillment_order_id,
        shipments.carrier_id,

        ---------- text
        shipments.tracking_number,
        shipments.status,

        ---------- numerics
        coalesce(item_summary.line_item_count, 0) as line_item_count,
        coalesce(item_summary.total_quantity, 0) as total_quantity,
        coalesce(attempts.delivery_attempt_count, 0) as delivery_attempt_count,

        ---------- timestamps
        shipments.shipped_at,
        shipments.estimated_delivery_at,
        delivered_event.delivered_at,
        timestamp_diff(delivered_event.delivered_at, shipments.shipped_at, hour) as hours_to_deliver,

        ---------- booleans
        delivered_event.delivered_at is not null
            and delivered_event.delivered_at > shipments.estimated_delivery_at as was_late

    from shipments
    left join item_summary on shipments.shipment_id = item_summary.shipment_id
    left join delivered_event on shipments.shipment_id = delivered_event.shipment_id
    left join attempts on shipments.shipment_id = attempts.shipment_id

)

select * from final
