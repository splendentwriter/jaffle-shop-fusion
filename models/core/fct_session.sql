with

sessions as (

    select * from {{ ref('stg_sessions') }}

),

events as (

    select * from {{ ref('stg_web_events') }}

),

event_summary as (

    select
        session_id,
        count(*) as event_count,
        countif(event_type = 'product_view') > 0 as has_product_view,
        countif(event_type = 'search') > 0 as has_search,
        countif(event_type = 'add_to_cart') > 0 as has_add_to_cart

    from events
    group by session_id

),

final as (

    select

        ----------  ids
        sessions.session_id,
        sessions.customer_id,
        sessions.device_id,

        ---------- timestamps
        sessions.started_at,
        sessions.ended_at,
        timestamp_diff(sessions.ended_at, sessions.started_at, second) as duration_seconds,

        ---------- text
        sessions.landing_page,
        sessions.referrer_source,

        ---------- booleans
        sessions.is_authenticated,
        coalesce(event_summary.has_product_view, false) as has_product_view,
        coalesce(event_summary.has_search, false) as has_search,
        coalesce(event_summary.has_add_to_cart, false) as has_add_to_cart,

        ---------- numerics
        coalesce(event_summary.event_count, 0) as event_count

    from sessions
    left join event_summary on sessions.session_id = event_summary.session_id

)

select * from final
