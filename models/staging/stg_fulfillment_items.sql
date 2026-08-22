with

source as (

    select * from {{ source('ecom', 'raw_fulfillment_items') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as fulfillment_item_id,
        fulfillment_order_id,
        sku as product_id,

        ---------- numerics
        quantity

    from source

)

select * from renamed
