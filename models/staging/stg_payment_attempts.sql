with

source as (

    select * from {{ source('ecom', 'raw_payment_attempts') }}

),

renamed as (

    select

        ----------  ids
        id as payment_attempt_id,
        checkout_id,
        nullif(payment_method_id, '') as payment_method_id,

        ---------- text
        status,
        nullif(decline_reason, '') as decline_reason,

        ---------- numerics
        amount_cents,
        {{ cents_to_dollars('amount_cents') }} as amount,

        ---------- timestamps
        attempted_at

    from source

)

select * from renamed
