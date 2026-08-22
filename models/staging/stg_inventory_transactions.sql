with

source as (

    select * from {{ source('ecom', 'raw_inventory_transactions') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as inventory_transaction_id,
        warehouse_id,
        sku as product_id,

        ---------- text
        transaction_type,
        nullif(adjustment_reason, '') as adjustment_reason,

        ---------- numerics
        quantity_delta,

        ---------- timestamps
        occurred_at

    from source

)

select * from renamed
