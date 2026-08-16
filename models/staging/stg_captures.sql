with

source as (

    select * from {{ source('ecom', 'raw_captures') }}

),

renamed as (

    select

        ----------  ids
        id as capture_id,
        authorization_id,

        ---------- numerics
        amount_cents,
        {{ cents_to_dollars('amount_cents') }} as amount,

        ---------- timestamps
        captured_at

    from source

)

select * from renamed
