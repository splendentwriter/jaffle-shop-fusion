with

source as (

    select * from {{ source('ecom', 'raw_checkout_events') }}

),

renamed as (

    select

        ----------  ids
        id as checkout_event_id,
        checkout_id,

        ---------- text
        event_type,

        ---------- timestamps
        occurred_at

    from source

)

select * from renamed
