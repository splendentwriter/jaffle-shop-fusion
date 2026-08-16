with

levels as (

    select * from {{ ref('dim_inventory_level') }}
    where is_current

),

-- only 'held' reservations reduce sellable availability here: 'committed'
-- reservations assume the corresponding sale has already been posted to
-- stg_inventory_transactions (and so is already netted into
-- quantity_on_hand), and 'released'/'expired' no longer hold anything.
-- Note: this seed data has no reservations left in 'held' status - every
-- checkout in it already resolved to a terminal state - so held_quantity
-- is 0 for all rows today. The mechanism is real; there's just no
-- in-flight checkout in this snapshot to exercise it.
held_reservations as (

    select
        warehouse_id,
        product_id,
        sum(cast(quantity as int64)) as held_quantity

    from {{ ref('stg_stock_reservations') }}
    where status = 'held'
    group by 1, 2

),

final as (

    select

        ----------  ids
        levels.warehouse_id,
        levels.product_id,

        ---------- numerics
        levels.quantity_on_hand,
        levels.reorder_point,
        coalesce(held_reservations.held_quantity, 0) as held_quantity,
        levels.quantity_on_hand - coalesce(held_reservations.held_quantity, 0) as available_quantity,

        ---------- booleans
        levels.quantity_on_hand <= levels.reorder_point as is_below_reorder_point

    from levels
    left join held_reservations
        on levels.warehouse_id = held_reservations.warehouse_id
        and levels.product_id = held_reservations.product_id

)

select * from final
