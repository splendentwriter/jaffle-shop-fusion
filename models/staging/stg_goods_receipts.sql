with

source as (

    select * from {{ source('ecom', 'raw_goods_receipts') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as goods_receipt_id,
        purchase_order_id,
        sku as product_id,

        ---------- text
        condition,

        ---------- numerics
        quantity_received,

        ---------- timestamps
        received_at

    from source

)

select * from renamed
