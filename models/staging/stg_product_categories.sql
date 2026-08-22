with

source as (

    select * from {{ source('ecom', 'raw_product_categories') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as category_id,
        nullif(parent_category_id, '') as parent_category_id,

        ---------- text
        category_name

    from source

)

select * from renamed
