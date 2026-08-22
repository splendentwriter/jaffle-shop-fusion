with

source as (

    select * from {{ source('ecom', 'raw_payouts') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as payout_id,

        ---------- text
        status,
        bank_reference,

        ---------- numerics
        amount_cents,
        {{ cents_to_dollars('amount_cents') }} as amount,

        ---------- timestamps
        period_start,
        period_end,
        payout_date

    from source

)

select * from renamed
