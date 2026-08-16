with

source as (

    select * from {{ source('ecom', 'raw_product_images') }}

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
