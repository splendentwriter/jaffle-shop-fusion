with

source as (

    select * from {{ source('ecom', 'raw_ticket_events') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as ticket_event_id,
        ticket_id,

        ---------- text
        event_type,
        nullif(detail, '') as detail,

        ---------- timestamps
        occurred_at

    from source

)

select * from renamed
