with

source as (

    select * from {{ source('ecom', 'raw_authorizations') }}

),

renamed as (

    select

        ----------  ids
        id as authorization_id,
        payment_attempt_id,

        ---------- text
        status,

        ---------- numerics
        amount_cents,
        {{ cents_to_dollars('amount_cents') }} as amount,

        ---------- timestamps
        authorized_at

    from source

)

select * from renamed
