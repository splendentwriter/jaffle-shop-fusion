with

gift_cards as (

    select * from {{ ref('stg_gift_cards') }}

),

transactions as (

    select * from {{ ref('stg_gift_card_transactions') }}

),

transaction_summary as (

    select
        gift_card_id,
        sum(case when transaction_type = 'issue' then amount_cents else 0 end) as issued_cents,
        sum(case when transaction_type = 'redeem' then -amount_cents else 0 end) as redeemed_cents,
        sum(case when transaction_type = 'refund_credit' then amount_cents else 0 end) as credited_cents,
        sum(case when transaction_type = 'expire' then -amount_cents else 0 end) as expired_cents,
        countif(transaction_type = 'redeem') as redemption_count

    from transactions
    group by 1

),

final as (

    select

        ----------  ids
        gift_cards.gift_card_id,
        gift_cards.purchased_by_customer_id,

        ---------- text
        gift_cards.code,
        gift_cards.status,

        ---------- numerics
        gift_cards.current_balance_cents,
        coalesce(transaction_summary.issued_cents, 0) as issued_cents,
        coalesce(transaction_summary.redeemed_cents, 0) as redeemed_cents,
        coalesce(transaction_summary.credited_cents, 0) as credited_cents,
        coalesce(transaction_summary.expired_cents, 0) as expired_cents,
        coalesce(transaction_summary.redemption_count, 0) as redemption_count,

        ---------- timestamps
        gift_cards.issued_at,
        gift_cards.expires_at

    from gift_cards
    left join transaction_summary on gift_cards.gift_card_id = transaction_summary.gift_card_id

)

select * from final
