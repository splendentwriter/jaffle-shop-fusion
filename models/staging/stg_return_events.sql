with

source as (

    select * from {{ source('ecom', 'raw_return_events') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as return_event_id,
        return_id,

        ---------- text
        event_type,

        ---------- timestamps
        occurred_at

    from source

)

select * from renamed
