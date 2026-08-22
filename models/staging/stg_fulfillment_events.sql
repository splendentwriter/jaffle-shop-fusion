with

source as (

    select * from {{ source('ecom', 'raw_fulfillment_events') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as fulfillment_event_id,
        fulfillment_order_id,

        ---------- text
        event_type,

        ---------- timestamps
        occurred_at

    from source

)

select * from renamed
