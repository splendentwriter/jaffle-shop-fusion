with

product_history as (

    select * from {{ ref('products_snapshot') }}

),

brands as (

    select * from {{ ref('stg_product_brands') }}

),

attributes as (

    select * from {{ ref('int_product_attributes') }}

),

final as (

    select

        ----------  ids
        product_history.product_id,
        brands.brand_id,

        ---------- text
        product_history.product_name,
        product_history.product_type,
        product_history.product_description,
        attributes.spice_level,
        attributes.allergens,

        ---------- numerics
        product_history.product_price,
        attributes.calories,

        ---------- booleans
        product_history.is_food_item,
        product_history.is_drink_item,
        attributes.is_vegetarian,

        ---------- scd2 tracking
        product_history.dbt_valid_from as valid_from,
        product_history.dbt_valid_to as valid_to,
        product_history.dbt_valid_to is null as is_current

    from product_history
    left join brands on product_history.product_id = brands.product_id
    left join attributes on product_history.product_id = attributes.product_id

)

select * from final
