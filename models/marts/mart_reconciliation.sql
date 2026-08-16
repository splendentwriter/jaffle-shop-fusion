with

reconciliation as (

    select * from {{ ref('fct_payout_reconciliation') }}

),

final as (

    select

        ----------  ids
        payout_id,

        ---------- text
        status,

        ---------- numerics
        round(payout_amount_cents / 100.0, 2) as payout_amount,
        round(computed_net_cents / 100.0, 2) as computed_net_amount,
        round(discrepancy_cents / 100.0, 2) as discrepancy_amount,
        capture_count,

        ---------- timestamps
        period_start,
        period_end,

        ---------- booleans
        is_reconciled

    from reconciliation

)

select * from final
