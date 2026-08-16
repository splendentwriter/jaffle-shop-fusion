with

positions as (

    select * from {{ ref('fct_inventory_position') }}

),

products as (

    select * from {{ ref('dim_product') }}
    where is_current

),

warehouses as (

    select * from {{ ref('stg_warehouses') }}

),

final as (

    select

        ----------  ids
        positions.warehouse_id,
        positions.product_id,

        ---------- text
        products.product_name,
        warehouses.warehouse_name,
        warehouses.region,

        ---------- numerics
        positions.quantity_on_hand,
        positions.reorder_point,
        positions.held_quantity,
        positions.available_quantity,

        ---------- booleans
        positions.is_below_reorder_point

    from positions
    left join products on positions.product_id = products.product_id
    left join warehouses on positions.warehouse_id = warehouses.warehouse_id

)

select * from final
