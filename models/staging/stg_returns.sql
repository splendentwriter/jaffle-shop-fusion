with

source as (

    select * from {{ source('ecom', 'raw_returns') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as return_id,
        shipment_id,
        customer_id,

        ---------- text
        reason,
        status,
        refund_status,

        ---------- numerics
        refund_amount_cents,
        {{ cents_to_dollars('refund_amount_cents') }} as refund_amount,

        ---------- timestamps
        requested_at,
        refunded_at

    from source

)

select * from renamed
