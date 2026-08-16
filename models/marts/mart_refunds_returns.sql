with

returns as (

    select * from {{ ref('fct_return') }}

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
        returns.line_item_count,
        returns.total_quantity,
        returns.inspection_count,
        returns.resellable_count,
        round(returns.refund_amount_cents / 100.0, 2) as refund_amount,
        timestamp_diff(returns.refunded_at, returns.requested_at, hour) as hours_to_refund,

        ---------- timestamps
        returns.requested_at,
        returns.refunded_at,

        ---------- booleans
        returns.is_refunded,
        returns.inspection_count > 0
            and returns.resellable_count < returns.inspection_count as has_unsellable_items

    from returns

)

select * from final
