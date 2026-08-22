with

source as (

    select * from {{ source('ecom', 'raw_cart_events') }}
    {{ limit_in_dev() }}

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
