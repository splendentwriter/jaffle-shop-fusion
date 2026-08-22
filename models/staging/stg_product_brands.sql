with

source as (

    select * from {{ source('ecom', 'raw_product_brands') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        sku as product_id,
        nullif(brand_id, '') as brand_id

    from source

)

select * from renamed
