with

source as (

    select * from {{ source('ecom', 'raw_disputes') }}

),

renamed as (

    select

        ----------  ids
        id as dispute_id,
        payment_attempt_id,

        ---------- text
        reason,
        status,

        ---------- numerics
        amount_cents,
        {{ cents_to_dollars('amount_cents') }} as amount,

        ---------- timestamps
        opened_at

    from source

)

select * from renamed
