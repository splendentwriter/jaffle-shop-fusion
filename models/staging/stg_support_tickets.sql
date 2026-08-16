with

source as (

    select * from {{ source('ecom', 'raw_support_tickets') }}

),

renamed as (

    select

        ----------  ids
        id as ticket_id,
        customer_id,
        nullif(agent_id, '') as agent_id,
        nullif(related_return_id, '') as related_return_id,

        ---------- text
        category,
        subject,
        status,
        priority,

        ---------- timestamps
        created_at,
        resolved_at

    from source

)

select * from renamed
