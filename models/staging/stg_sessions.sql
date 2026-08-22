with

source as (

    select * from {{ source('ecom', 'raw_sessions') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as session_id,
        nullif(customer_id, '') as customer_id,
        nullif(device_id, '') as device_id,

        ---------- timestamps
        started_at,
        ended_at,

        ---------- text
        landing_page,
        referrer_source,

        ---------- booleans
        is_authenticated

    from source

)

select * from renamed
