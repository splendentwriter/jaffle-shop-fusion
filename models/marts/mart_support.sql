with

tickets as (

    select * from {{ ref('fct_support_ticket') }}

),

agents as (

    select * from {{ ref('stg_support_agents') }}

),

final as (

    select

        ----------  ids
        tickets.ticket_id,
        tickets.customer_id,
        tickets.agent_id,
        tickets.related_return_id,

        ---------- text
        agents.agent_name,
        agents.team,
        tickets.category,
        tickets.status,
        tickets.priority,

        ---------- numerics
        tickets.message_count,
        tickets.customer_message_count,
        tickets.agent_message_count,
        tickets.reopen_count,
        tickets.hours_to_resolve,

        ---------- timestamps
        tickets.created_at,
        tickets.resolved_at,

        ---------- booleans
        tickets.is_assigned,
        tickets.is_resolved,
        tickets.reopen_count > 0 as was_reopened

    from tickets
    left join agents on tickets.agent_id = agents.agent_id

)

select * from final
