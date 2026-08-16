with

category_map as (

    select * from {{ ref('stg_product_category_map') }}

),

final as (

    select
        product_id,
        category_id

    from category_map

)

select * from final
