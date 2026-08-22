with

source as (

    select * from {{ source('ecom', 'raw_product_images') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as image_id,
        sku as product_id,

        ---------- text
        image_url,

        ---------- numerics
        sort_order,

        ---------- booleans
        is_primary

    from source

)

select * from renamed
