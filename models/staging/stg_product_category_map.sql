with

source as (

    select * from {{ source('ecom', 'raw_product_category_map') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        sku as product_id,
        category_id

    from source

)

select * from renamed
