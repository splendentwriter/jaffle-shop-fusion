with

source as (

    select * from {{ source('ecom', 'raw_shipment_items') }}

),

renamed as (

    select

        ----------  ids
        id as shipment_item_id,
        shipment_id,
        sku as product_id,

        ---------- numerics
        quantity

    from source

)

select * from renamed
