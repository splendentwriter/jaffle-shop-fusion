with

source as (

    select * from {{ source('ecom', 'raw_support_messages') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as support_message_id,
        ticket_id,

        ---------- text
        sender_type,
        body,

        ---------- timestamps
        sent_at

    from source

)

select * from renamed
