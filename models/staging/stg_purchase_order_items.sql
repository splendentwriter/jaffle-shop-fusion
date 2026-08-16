with

source as (

    select * from {{ source('ecom', 'raw_purchase_order_items') }}

),

renamed as (

    select

        ----------  ids
        id as purchase_order_item_id,
        purchase_order_id,
        sku as product_id,

        ---------- numerics
        quantity_ordered,
        unit_cost_cents,
        {{ cents_to_dollars('unit_cost_cents') }} as unit_cost

    from source

)

select * from renamed
