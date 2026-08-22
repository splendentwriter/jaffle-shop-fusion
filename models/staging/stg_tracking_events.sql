with

source as (

    select * from {{ source('ecom', 'raw_tracking_events') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as tracking_event_id,
        shipment_id,

        ---------- text
        event_type,
        location,

        ---------- timestamps
        occurred_at

    from source

)

select * from renamed
