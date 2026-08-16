with

source as (

    select * from {{ source('ecom', 'raw_inventory_levels') }}

),

renamed as (

    select

        ----------  ids
        id as inventory_level_id,
        warehouse_id,
        sku as product_id,

        ---------- numerics
        quantity_on_hand,
        reorder_point,

        ---------- timestamps
        updated_at

    from source

)

select * from renamed
