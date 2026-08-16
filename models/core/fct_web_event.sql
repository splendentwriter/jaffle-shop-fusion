{{
    config(
        materialized='incremental',
        unique_key='event_id',
        on_schema_change='sync_all_columns',
        partition_by={'field': 'event_date', 'data_type': 'date'},
        cluster_by=['event_type'],
    )
}}

with

events as (

    select * from {{ ref('stg_web_events') }}

    {% if is_incremental() %}
    where occurred_at > (select max(occurred_at) from {{ this }})
    {% endif %}

),

sessions as (

    select * from {{ ref('stg_sessions') }}

),

final as (

    select

        ----------  ids
        events.event_id,
        events.session_id,
        sessions.customer_id,
        events.product_id,

        ---------- text
        events.event_type,
        events.page_url,
        events.search_query,

        ---------- timestamps
        events.occurred_at,
        date(events.occurred_at) as event_date,

        ---------- booleans
        sessions.is_authenticated

    from events
    left join sessions on events.session_id = sessions.session_id

)

select * from final
