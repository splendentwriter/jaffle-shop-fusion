with

cart_items as (

    select * from {{ ref('stg_cart_items') }}

),

current_products as (

    select * from {{ ref('dim_product') }}
    where is_current

),

final as (

    select

        ----------  ids
        cart_items.cart_item_id,
        cart_items.cart_id,
        cart_items.product_id,

        ---------- numerics
        cart_items.quantity,
        cart_items.unit_price as unit_price_at_add,
        current_products.product_price as current_unit_price,
        current_products.product_price - cart_items.unit_price as price_drift,
        -- not clamped to zero for the known non-positive-quantity rows —
        -- see stg_cart_items' warn-severity quantity check
        cart_items.quantity * cart_items.unit_price as line_total,

        ---------- timestamps
        cart_items.added_at,
        cart_items.removed_at,

        ---------- booleans
        cart_items.removed_at is not null as is_removed,
        cart_items.is_saved_for_later,
        current_products.product_id is not null as is_still_in_catalogue

    from cart_items
    left join current_products on cart_items.product_id = current_products.product_id

)

select * from final
