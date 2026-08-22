with

source as (

    select * from {{ source('ecom', 'raw_stock_reservations') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as reservation_id,
        warehouse_id,
        sku as product_id,
        checkout_id,

        ---------- text
        status,

        ---------- numerics
        quantity,

        ---------- timestamps
        reserved_at,
        released_at

    from source

)

select * from renamed
