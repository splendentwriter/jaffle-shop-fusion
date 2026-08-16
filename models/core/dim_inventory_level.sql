with

level_history as (

    select * from {{ ref('inventory_levels_snapshot') }}

),

final as (

    select

        ----------  ids
        warehouse_id,
        product_id,

        ---------- numerics
        quantity_on_hand,
        reorder_point,

        ---------- scd2 tracking
        dbt_valid_from as valid_from,
        dbt_valid_to as valid_to,
        dbt_valid_to is null as is_current

    from level_history

)

select * from final
