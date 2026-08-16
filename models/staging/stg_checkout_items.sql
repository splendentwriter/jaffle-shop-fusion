with

source as (

    select * from {{ source('ecom', 'raw_checkout_items') }}

),

renamed as (

    select

        ----------  ids
        id as checkout_item_id,
        checkout_id,
        sku as product_id,

        ---------- numerics
        quantity,
        unit_price_cents,
        {{ cents_to_dollars('unit_price_cents') }} as unit_price

    from source

)

select * from renamed
