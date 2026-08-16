with

items as (

    select * from {{ ref('stg_purchase_order_items') }}

),

receipts as (

    select * from {{ ref('stg_goods_receipts') }}

),

-- a purchase order never orders the same sku twice (see the generator), so
-- (purchase_order_id, product_id) safely identifies one item's receipts
receipt_summary as (

    select
        purchase_order_id,
        product_id,
        sum(quantity_received) as quantity_received,
        countif(condition != 'good') as quality_issue_count

    from receipts
    group by 1, 2

),

final as (

    select

        ----------  ids
        items.purchase_order_item_id,
        items.purchase_order_id,
        items.product_id,

        ---------- numerics
        items.quantity_ordered,
        items.unit_cost_cents,
        items.quantity_ordered * items.unit_cost_cents as ordered_value_cents,
        coalesce(receipt_summary.quantity_received, 0) as quantity_received,
        items.quantity_ordered - coalesce(receipt_summary.quantity_received, 0) as quantity_outstanding,
        coalesce(receipt_summary.quality_issue_count, 0) as quality_issue_count,
        safe_divide(coalesce(receipt_summary.quantity_received, 0), items.quantity_ordered) as fill_rate

    from items
    left join receipt_summary
        on items.purchase_order_id = receipt_summary.purchase_order_id
        and items.product_id = receipt_summary.product_id

)

select * from final
