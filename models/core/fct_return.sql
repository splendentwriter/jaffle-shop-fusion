with

returns as (

    select * from {{ ref('stg_returns') }}

),

items as (

    select * from {{ ref('stg_return_items') }}

),

item_summary as (

    select
        return_id,
        count(*) as line_item_count,
        sum(quantity) as total_quantity

    from items
    group by 1

),

inspections as (

    select
        items.return_id,
        count(*) as inspection_count,
        countif(inspections.inspection_result = 'resellable') as resellable_count

    from {{ ref('stg_return_inspections') }} as inspections
    inner join items on inspections.return_item_id = items.return_item_id
    group by 1

),

final as (

    select

        ----------  ids
        returns.return_id,
        returns.shipment_id,
        returns.customer_id,

        ---------- text
        returns.reason,
        returns.status,
        returns.refund_status,

        ---------- numerics
        coalesce(item_summary.line_item_count, 0) as line_item_count,
        coalesce(item_summary.total_quantity, 0) as total_quantity,
        coalesce(inspections.inspection_count, 0) as inspection_count,
        coalesce(inspections.resellable_count, 0) as resellable_count,
        returns.refund_amount_cents,

        ---------- timestamps
        returns.requested_at,
        returns.refunded_at,

        ---------- booleans
        returns.refund_status = 'completed' as is_refunded

    from returns
    left join item_summary on returns.return_id = item_summary.return_id
    left join inspections on returns.return_id = inspections.return_id

)

select * from final
