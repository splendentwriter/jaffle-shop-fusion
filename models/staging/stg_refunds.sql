with

source as (

    select * from {{ source('ecom', 'raw_refunds') }}

),

renamed as (

    select

        ----------  ids
        id as refund_id,
        capture_id,

        ---------- text
        status,
        reason,

        ---------- numerics
        amount_cents,
        {{ cents_to_dollars('amount_cents') }} as amount,

        ---------- timestamps
        requested_at,
        refunded_at

    from source

)

select * from renamed
