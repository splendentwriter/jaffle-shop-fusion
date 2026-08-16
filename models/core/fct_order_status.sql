with

status_history as (

    select * from {{ ref('stg_order_status_history') }}

),

-- orphaned rows (order_id no longer resolves to an order - see
-- stg_order_status_history's warn-severity test) are excluded here via the
-- inner join in `final`, same treatment as dim_customer's orphan accounts
latest_status as (

    select
        order_id,
        status,
        occurred_at,
        row_number() over (partition by order_id order by occurred_at desc) as recency_rank

    from status_history

),

status_summary as (

    select
        order_id,
        count(*) as status_change_count,
        min(occurred_at) as first_status_at,
        max(occurred_at) as last_status_at

    from status_history
    group by order_id

),

final as (

    select

        ----------  ids
        orders.order_id,

        ---------- text
        latest_status.status as current_status,

        ---------- numerics
        status_summary.status_change_count,

        ---------- timestamps
        status_summary.first_status_at,
        status_summary.last_status_at,

        ---------- booleans
        latest_status.status = 'cancelled' as is_cancelled

    from {{ ref('stg_orders') }} as orders
    inner join latest_status on orders.order_id = latest_status.order_id and latest_status.recency_rank = 1
    inner join status_summary on orders.order_id = status_summary.order_id

)

select * from final
