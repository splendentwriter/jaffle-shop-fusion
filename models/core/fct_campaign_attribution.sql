with

click_events as (

    select * from {{ ref('stg_marketing_events') }}
    where event_type in ('clicked', 'click')

),

completed_checkouts as (

    select * from {{ ref('stg_checkouts') }}
    where status = 'completed'

),

-- last-touch attribution: the most recent marketing click for the same
-- customer within 7 days before the checkout started gets the credit
touches_before_checkout as (

    select
        completed_checkouts.checkout_id,
        completed_checkouts.customer_id,
        completed_checkouts.started_at as checkout_started_at,
        click_events.campaign_id,
        click_events.channel,
        click_events.occurred_at as touch_at,
        row_number() over (
            partition by completed_checkouts.checkout_id
            order by click_events.occurred_at desc
        ) as touch_recency_rank

    from completed_checkouts
    inner join click_events
        on completed_checkouts.customer_id = click_events.customer_id
        and click_events.occurred_at <= completed_checkouts.started_at
        and click_events.occurred_at >= timestamp_sub(completed_checkouts.started_at, interval 7 day)

),

final as (

    select

        ----------  ids
        checkout_id,
        customer_id,
        campaign_id,

        ---------- text
        channel,

        ---------- timestamps
        touch_at,
        checkout_started_at,

        ---------- numerics
        timestamp_diff(checkout_started_at, touch_at, hour) as hours_between_touch_and_checkout

    from touches_before_checkout
    where touch_recency_rank = 1

)

select * from final
