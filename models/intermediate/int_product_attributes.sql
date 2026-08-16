with

attributes as (

    select * from {{ ref('stg_product_attributes') }}

),

-- pivot the EAV rows into one column per known attribute. Where a product
-- has more than one value for the same attribute_name (a known upstream
-- re-entry issue - see stg_product_attributes), max() deterministically
-- picks one value; which one is arbitrary and not a claim about recency.
pivoted as (

    select
        product_id,
        max(case when attribute_name = 'is_vegetarian' then attribute_value end) as is_vegetarian,
        max(case when attribute_name = 'spice_level' then attribute_value end) as spice_level,
        max(case when attribute_name = 'calories' then attribute_value end) as calories,
        max(case when attribute_name = 'allergens' then attribute_value end) as allergens

    from attributes
    group by product_id

),

final as (

    select
        product_id,
        is_vegetarian = 'true' as is_vegetarian,
        spice_level,
        cast(calories as int64) as calories,
        allergens

    from pivoted

)

select * from final
