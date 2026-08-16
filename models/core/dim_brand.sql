with

brands as (

    select * from {{ ref('stg_brands') }}

),

final as (

    select
        brand_id,
        brand_name,
        brand_description

    from brands

)

select * from final
