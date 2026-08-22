with

source as (

    select * from {{ source('ecom', 'raw_cart_items') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as cart_item_id,
        cart_id,
        sku as product_id,

        ---------- numerics
        quantity,
        unit_price_cents,
        {{ cents_to_dollars('unit_price_cents') }} as unit_price,

        ---------- timestamps
        added_at,
        removed_at,

        ---------- booleans
        is_saved_for_later

    from source

)

select * from renamed
