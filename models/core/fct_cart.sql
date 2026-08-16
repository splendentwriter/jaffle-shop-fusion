with

carts as (

    select * from {{ ref('stg_carts') }}

),

items as (

    select * from {{ ref('fct_cart_item') }}

),

item_summary as (

    select
        cart_id,
        count(*) as line_item_count,
        sum(case when removed_at is null and not is_saved_for_later then quantity else 0 end) as active_quantity,
        sum(case when removed_at is null and not is_saved_for_later then line_total else 0 end) as cart_subtotal_cents,
        countif(is_saved_for_later) as saved_for_later_count

    from items
    group by cart_id

),

final as (

    select

        ----------  ids
        carts.cart_id,
        carts.customer_id,
        carts.session_id,

        ---------- text
        carts.status,

        ---------- timestamps
        carts.created_at,
        carts.updated_at,

        ---------- numerics
        coalesce(item_summary.line_item_count, 0) as line_item_count,
        coalesce(item_summary.active_quantity, 0) as active_quantity,
        coalesce(item_summary.cart_subtotal_cents, 0) as cart_subtotal_cents,
        coalesce(item_summary.saved_for_later_count, 0) as saved_for_later_count,

        ---------- booleans
        carts.status = 'abandoned' as is_abandoned

    from carts
    left join item_summary on carts.cart_id = item_summary.cart_id

)

select * from final
