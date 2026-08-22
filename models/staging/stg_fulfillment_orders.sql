with

source as (

    select * from {{ source('ecom', 'raw_fulfillment_orders') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as fulfillment_order_id,
        checkout_id,
        warehouse_id,

        ---------- text
        status,

        ---------- timestamps
        created_at,
        completed_at

    from source

)

select * from renamed
