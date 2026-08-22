with

source as (

    select * from {{ source('ecom', 'raw_gift_card_transactions') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as gift_card_transaction_id,
        gift_card_id,
        nullif(related_checkout_id, '') as related_checkout_id,

        ---------- text
        transaction_type,

        ---------- numerics
        amount_cents,
        {{ cents_to_dollars('amount_cents') }} as amount,

        ---------- timestamps
        occurred_at

    from source

)

select * from renamed
