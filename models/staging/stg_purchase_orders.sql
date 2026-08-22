with

source as (

    select * from {{ source('ecom', 'raw_purchase_orders') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as purchase_order_id,
        supplier_id,
        warehouse_id,

        ---------- text
        status,

        ---------- timestamps
        ordered_at,
        expected_at

    from source

)

select * from renamed
