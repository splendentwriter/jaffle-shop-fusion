with

payouts as (

    select * from {{ ref('stg_payouts') }}

),

transaction_fees as (

    select * from {{ ref('fct_transaction_fee') }}

),

period_totals as (

    select
        payouts.payout_id,
        sum(transaction_fees.net_amount_cents) as computed_net_cents,
        count(*) as capture_count

    from payouts
    left join transaction_fees
        on transaction_fees.captured_at >= payouts.period_start
        and transaction_fees.captured_at < payouts.period_end
    group by 1

),

final as (

    select

        ----------  ids
        payouts.payout_id,

        ---------- text
        payouts.status,

        ---------- numerics
        payouts.amount_cents as payout_amount_cents,
        coalesce(period_totals.computed_net_cents, 0) as computed_net_cents,
        coalesce(period_totals.capture_count, 0) as capture_count,
        payouts.amount_cents - coalesce(period_totals.computed_net_cents, 0) as discrepancy_cents,

        ---------- timestamps
        payouts.period_start,
        payouts.period_end,

        ---------- booleans
        -- a 1-cent tolerance absorbs independent rounding between the
        -- payout batch total and the per-capture fee recompute here
        abs(payouts.amount_cents - coalesce(period_totals.computed_net_cents, 0)) <= 1 as is_reconciled

    from payouts
    left join period_totals on payouts.payout_id = period_totals.payout_id

)

select * from final
