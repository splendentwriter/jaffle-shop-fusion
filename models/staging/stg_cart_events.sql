with

source as (

    select * from {{ source('ecom', 'raw_cart_events') }}

),

renamed as (

    select

        ----------  ids
        id as cart_event_id,
        cart_id,

        ---------- text
        event_type,

        ---------- timestamps
        occurred_at

    from source

)

select * from renamed
