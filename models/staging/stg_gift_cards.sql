with

source as (

    select * from {{ source('ecom', 'raw_gift_cards') }}

),

renamed as (

    select

        ----------  ids
        id as gift_card_id,
        nullif(purchased_by_customer_id, '') as purchased_by_customer_id,

        ---------- text
        code,
        status,

        ---------- numerics
        initial_balance_cents,
        current_balance_cents,
        {{ cents_to_dollars('initial_balance_cents') }} as initial_balance,
        {{ cents_to_dollars('current_balance_cents') }} as current_balance,

        ---------- timestamps
        issued_at,
        expires_at

    from source

)

select * from renamed
