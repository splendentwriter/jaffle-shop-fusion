with

attempts as (

    select * from {{ ref('stg_payment_attempts') }}

),

authorizations as (

    select * from {{ ref('stg_authorizations') }}

),

captures as (

    select * from {{ ref('stg_captures') }}

),

refunds as (

    select * from {{ ref('stg_refunds') }}

),

disputes as (

    select * from {{ ref('stg_disputes') }}

),

capture_by_attempt as (

    select
        authorizations.payment_attempt_id,
        captures.capture_id,
        captures.amount_cents as captured_amount_cents

    from authorizations
    inner join captures on authorizations.authorization_id = captures.authorization_id

),

refund_by_attempt as (

    select
        capture_by_attempt.payment_attempt_id,
        sum(refunds.amount_cents) as refunded_amount_cents

    from refunds
    inner join capture_by_attempt on refunds.capture_id = capture_by_attempt.capture_id
    where refunds.status = 'completed'
    group by 1

),

dispute_by_attempt as (

    select
        payment_attempt_id,
        count(*) as dispute_count,
        countif(status = 'chargeback') > 0 as has_chargeback,
        -- arbitrary but deterministic pick when an attempt has more than one dispute
        max(status) as latest_dispute_status

    from disputes
    group by 1

),

final as (

    select

        ----------  ids
        attempts.payment_attempt_id,
        attempts.checkout_id,
        attempts.payment_method_id,

        ---------- text
        attempts.status as attempt_status,
        attempts.decline_reason,
        dispute_by_attempt.latest_dispute_status,

        ---------- numerics
        attempts.amount_cents as attempted_amount_cents,
        coalesce(capture_by_attempt.captured_amount_cents, 0) as captured_amount_cents,
        coalesce(refund_by_attempt.refunded_amount_cents, 0) as refunded_amount_cents,
        coalesce(capture_by_attempt.captured_amount_cents, 0)
            - coalesce(refund_by_attempt.refunded_amount_cents, 0) as net_amount_cents,
        coalesce(dispute_by_attempt.dispute_count, 0) as dispute_count,

        ---------- timestamps
        attempts.attempted_at,

        ---------- booleans
        coalesce(dispute_by_attempt.has_chargeback, false) as has_chargeback

    from attempts
    left join capture_by_attempt on attempts.payment_attempt_id = capture_by_attempt.payment_attempt_id
    left join refund_by_attempt on attempts.payment_attempt_id = refund_by_attempt.payment_attempt_id
    left join dispute_by_attempt on attempts.payment_attempt_id = dispute_by_attempt.payment_attempt_id

)

select * from final
