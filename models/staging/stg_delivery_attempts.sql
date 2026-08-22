with

source as (

    select * from {{ source('ecom', 'raw_delivery_attempts') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as delivery_attempt_id,
        shipment_id,

        ---------- text
        outcome,

        ---------- numerics
        attempt_number,

        ---------- timestamps
        attempted_at

    from source

)

select * from renamed
