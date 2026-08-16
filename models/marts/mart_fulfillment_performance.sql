with

fulfillment as (

    select * from {{ ref('fct_fulfillment_order') }}

),

warehouses as (

    select * from {{ ref('stg_warehouses') }}

),

final as (

    select

        ----------  ids
        fulfillment.fulfillment_order_id,
        fulfillment.checkout_id,
        fulfillment.warehouse_id,

        ---------- text
        warehouses.warehouse_name,
        warehouses.region,
        fulfillment.status,

        ---------- numerics
        fulfillment.line_item_count,
        fulfillment.total_quantity,
        fulfillment.hours_to_ship,
        timestamp_diff(fulfillment.picking_completed_at, fulfillment.picking_started_at, minute)
            as picking_minutes,
        timestamp_diff(fulfillment.packing_completed_at, fulfillment.packing_started_at, minute)
            as packing_minutes,

        ---------- timestamps
        fulfillment.created_at,
        fulfillment.shipped_at,

        ---------- booleans
        fulfillment.is_shipped,
        fulfillment.is_cancelled

    from fulfillment
    left join warehouses on fulfillment.warehouse_id = warehouses.warehouse_id

)

select * from final
