with

payments as (

    select * from {{ ref('fct_payment') }}

),

methods as (

    select * from {{ ref('stg_payment_methods') }}

),

final as (

    select

        ----------  ids
        payments.payment_attempt_id,
        payments.checkout_id,
        payments.payment_method_id,

        ---------- text
        methods.method_type,
        methods.card_brand,
        payments.attempt_status,
        payments.decline_reason,
        payments.latest_dispute_status,

        ---------- numerics
        round(payments.attempted_amount_cents / 100.0, 2) as attempted_amount,
        round(payments.captured_amount_cents / 100.0, 2) as captured_amount,
        round(payments.refunded_amount_cents / 100.0, 2) as refunded_amount,
        round(payments.net_amount_cents / 100.0, 2) as net_amount,
        payments.dispute_count,

        ---------- timestamps
        payments.attempted_at,

        ---------- booleans
        payments.attempt_status = 'captured' as is_successful,
        payments.attempt_status = 'declined' as is_declined,
        payments.has_chargeback

    from payments
    left join methods on payments.payment_method_id = methods.payment_method_id

)

select * from final
