with

source as (

    select * from {{ source('ecom', 'raw_return_items') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as return_item_id,
        return_id,
        sku as product_id,

        ---------- text
        condition_reported,

        ---------- numerics
        quantity

    from source

)

select * from renamed
