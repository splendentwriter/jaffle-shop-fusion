with

completed_checkouts as (

    select * from {{ ref('stg_checkouts') }}
    where status = 'completed'

),

tax as (

    select * from {{ ref('fct_checkout_tax') }}

),

payments as (

    select * from {{ ref('fct_payment') }}

),

discounts as (

    select
        checkout_id,
        sum(discount_amount_cents) as discount_amount_cents

    from {{ ref('fct_coupon_redemption') }}
    group by 1

),

fees_by_checkout as (

    select
        payment_attempts.checkout_id,
        sum(fee.fee_cents) as processing_fee_cents

    from {{ ref('stg_payment_attempts') }} as payment_attempts
    inner join {{ ref('stg_authorizations') }} as authorizations
        on payment_attempts.payment_attempt_id = authorizations.payment_attempt_id
    inner join {{ ref('fct_transaction_fee') }} as fee
        on authorizations.authorization_id = fee.authorization_id
    group by 1

),

final as (

    select

        ----------  ids
        completed_checkouts.checkout_id,

        ---------- numerics
        coalesce(tax.items_subtotal_cents, 0) as items_subtotal_cents,
        coalesce(tax.tax_amount_cents, 0) as tax_amount_cents,
        completed_checkouts.shipping_cost_cents,
        coalesce(discounts.discount_amount_cents, 0) as discount_amount_cents,
        coalesce(payments.refunded_amount_cents, 0) as refunded_amount_cents,
        coalesce(fees_by_checkout.processing_fee_cents, 0) as processing_fee_cents,

        -- gross revenue excludes tax collected on behalf of the tax
        -- authority - that was never the business's money to begin with
        coalesce(tax.items_subtotal_cents, 0)
            + completed_checkouts.shipping_cost_cents
            - coalesce(discounts.discount_amount_cents, 0)
            - coalesce(payments.refunded_amount_cents, 0) as gross_revenue_cents,

        coalesce(tax.items_subtotal_cents, 0)
            + completed_checkouts.shipping_cost_cents
            - coalesce(discounts.discount_amount_cents, 0)
            - coalesce(payments.refunded_amount_cents, 0)
            - coalesce(fees_by_checkout.processing_fee_cents, 0) as net_revenue_cents

    from completed_checkouts
    left join tax on completed_checkouts.checkout_id = tax.checkout_id
    left join payments on completed_checkouts.checkout_id = payments.checkout_id
    left join discounts on completed_checkouts.checkout_id = discounts.checkout_id
    left join fees_by_checkout on completed_checkouts.checkout_id = fees_by_checkout.checkout_id

)

select * from final
