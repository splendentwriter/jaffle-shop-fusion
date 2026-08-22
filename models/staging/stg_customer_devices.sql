with

source as (

    select * from {{ source('ecom', 'raw_customer_devices') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as device_id,
        customer_id,

        ---------- text
        device_type,

        ---------- timestamps
        first_seen_at,
        last_seen_at,

        ---------- booleans
        is_active

    from source

)

select * from renamed
