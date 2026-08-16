with

source as (

    select * from {{ source('ecom', 'raw_shipments') }}

),

renamed as (

    select

        ----------  ids
        id as shipment_id,
        fulfillment_order_id,
        carrier_id,

        ---------- text
        tracking_number,
        status,

        ---------- timestamps
        shipped_at,
        estimated_delivery_at

    from source

)

select * from renamed
