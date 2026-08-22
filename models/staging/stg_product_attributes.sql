with

source as (

    select * from {{ source('ecom', 'raw_product_attributes') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as attribute_id,
        sku as product_id,

        ---------- text
        attribute_name,
        attribute_value

    from source

)

select * from renamed
