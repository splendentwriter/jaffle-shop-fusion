with

tickets as (

    select * from {{ ref('stg_support_tickets') }}

),

messages as (

    select * from {{ ref('stg_support_messages') }}

),

message_summary as (

    select
        ticket_id,
        count(*) as message_count,
        countif(sender_type = 'customer') as customer_message_count,
        countif(sender_type = 'agent') as agent_message_count,
        min(sent_at) as first_message_at,
        max(sent_at) as last_message_at

    from messages
    group by 1

),

events as (

    select * from {{ ref('stg_ticket_events') }}

),

reopen_summary as (

    select
        ticket_id,
        countif(event_type = 'reopened') as reopen_count

    from events
    group by 1

),

final as (

    select

        ----------  ids
        tickets.ticket_id,
        tickets.customer_id,
        tickets.agent_id,
        tickets.related_return_id,

        ---------- text
        tickets.category,
        tickets.status,
        tickets.priority,

        ---------- numerics
        coalesce(message_summary.message_count, 0) as message_count,
        coalesce(message_summary.customer_message_count, 0) as customer_message_count,
        coalesce(message_summary.agent_message_count, 0) as agent_message_count,
        coalesce(reopen_summary.reopen_count, 0) as reopen_count,

        ---------- timestamps
        tickets.created_at,
        tickets.resolved_at,
        timestamp_diff(tickets.resolved_at, tickets.created_at, hour) as hours_to_resolve,

        ---------- booleans
        tickets.agent_id is not null as is_assigned,
        tickets.status in ('resolved', 'closed') as is_resolved

    from tickets
    left join message_summary on tickets.ticket_id = message_summary.ticket_id
    left join reopen_summary on tickets.ticket_id = reopen_summary.ticket_id

)

select * from final
