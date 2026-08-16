with

products as (

    select * from {{ ref('dim_product') }}
    where is_current

),

images as (

    select distinct product_id from {{ ref('stg_product_images') }}

),

brands as (

    select product_id from {{ ref('stg_product_brands') }}
    where brand_id is not null

),

categories as (

    select distinct product_id from {{ ref('bridge_product_category') }}

),

inventory as (

    select
        product_id,
        sum(available_quantity) as total_available_quantity

    from {{ ref('fct_inventory_position') }}
    group by 1

),

final as (

    select

        ----------  ids
        products.product_id,

        ---------- text
        products.product_name,
        products.product_type,

        ---------- numerics
        products.product_price,
        coalesce(inventory.total_available_quantity, 0) as available_quantity,

        ---------- booleans
        products.product_description is not null and products.product_description != '' as has_description,
        images.product_id is not null as has_image,
        brands.product_id is not null as has_brand,
        categories.product_id is not null as has_category,
        products.product_price is null as is_missing_price,
        coalesce(inventory.total_available_quantity, 0) <= 0 as is_out_of_stock

    from products
    left join images on products.product_id = images.product_id
    left join brands on products.product_id = brands.product_id
    left join categories on products.product_id = categories.product_id
    left join inventory on products.product_id = inventory.product_id

)

select * from final
