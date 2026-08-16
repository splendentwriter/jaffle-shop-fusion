with

shipments as (

    select * from {{ ref('fct_shipment') }}

),

carriers as (

    select * from {{ ref('stg_carriers') }}

),

final as (

    select

        ----------  ids
        shipments.shipment_id,
        shipments.fulfillment_order_id,
        shipments.carrier_id,

        ---------- text
        carriers.carrier_name,
        shipments.tracking_number,
        shipments.status,

        ---------- numerics
        shipments.line_item_count,
        shipments.total_quantity,
        shipments.delivery_attempt_count,
        shipments.hours_to_deliver,

        ---------- timestamps
        shipments.shipped_at,
        shipments.estimated_delivery_at,
        shipments.delivered_at,

        ---------- booleans
        shipments.was_late,
        shipments.delivered_at is not null as is_delivered

    from shipments
    left join carriers on shipments.carrier_id = carriers.carrier_id

)

select * from final
