with

authorizations as (

    select * from {{ ref('stg_authorizations') }}

),

captures as (

    select * from {{ ref('stg_captures') }}

),

refunds as (

    select * from {{ ref('stg_refunds') }}

),

payment_attempts as (

    select * from {{ ref('stg_payment_attempts') }}

),

authorization_tx as (

    select
        authorization_id as source_id,
        payment_attempt_id,
        'authorization' as transaction_type,
        amount_cents,
        authorized_at as occurred_at

    from authorizations

),

capture_tx as (

    select
        captures.capture_id as source_id,
        authorizations.payment_attempt_id,
        'capture' as transaction_type,
        captures.amount_cents,
        captures.captured_at as occurred_at

    from captures
    inner join authorizations on captures.authorization_id = authorizations.authorization_id

),

refund_tx as (

    select
        refunds.refund_id as source_id,
        authorizations.payment_attempt_id,
        'refund' as transaction_type,
        -refunds.amount_cents as amount_cents,
        coalesce(refunds.refunded_at, refunds.requested_at) as occurred_at

    from refunds
    inner join captures on refunds.capture_id = captures.capture_id
    inner join authorizations on captures.authorization_id = authorizations.authorization_id
    -- only completed refunds move real money; pending/rejected refunds
    -- don't belong in a ledger of what actually happened
    where refunds.status = 'completed'

),

unioned as (

    select * from authorization_tx
    union all
    select * from capture_tx
    union all
    select * from refund_tx

),

final as (

    select

        ----------  ids
        {{ dbt_utils.generate_surrogate_key(['unioned.transaction_type', 'unioned.source_id']) }} as payment_transaction_id,
        unioned.source_id,
        unioned.payment_attempt_id,
        payment_attempts.checkout_id,

        ---------- text
        unioned.transaction_type,

        ---------- numerics
        unioned.amount_cents,

        ---------- timestamps
        unioned.occurred_at

    from unioned
    left join payment_attempts on unioned.payment_attempt_id = payment_attempts.payment_attempt_id

)

select * from final
