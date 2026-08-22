with

source as (

    select * from {{ source('ecom', 'raw_product_tags') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        sku as product_id,

        ---------- text
        tag

    from source

)

select * from renamed
