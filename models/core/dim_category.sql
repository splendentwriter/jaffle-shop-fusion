with

categories as (

    select * from {{ ref('stg_product_categories') }}

),

final as (

    select

        child.category_id,
        child.category_name,
        child.parent_category_id,
        parent.category_name as parent_category_name,
        child.parent_category_id is null as is_top_level,

        -- a non-null parent_category_id that doesn't resolve to a real
        -- category (see stg_product_categories' warn-severity relationship
        -- test) would otherwise look identical to a legitimate top-level
        -- category once parent_category_name goes null; flag it explicitly
        child.parent_category_id is not null and parent.category_id is null as has_orphaned_parent

    from categories as child
    left join categories as parent on child.parent_category_id = parent.category_id

)

select * from final
