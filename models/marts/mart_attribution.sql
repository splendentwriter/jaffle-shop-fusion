with

attribution as (

    select * from {{ ref('fct_campaign_attribution') }}

),

revenue as (

    select checkout_id, gross_revenue_cents from {{ ref('fct_revenue') }}

),

final as (

    select

        ----------  ids
        attribution.checkout_id,
        attribution.customer_id,
        attribution.campaign_id,

        ---------- text
        attribution.channel,

        ---------- numerics
        attribution.hours_between_touch_and_checkout,
        round(coalesce(revenue.gross_revenue_cents, 0) / 100.0, 2) as attributed_revenue,

        ---------- timestamps
        attribution.touch_at,
        attribution.checkout_started_at

    from attribution
    left join revenue on attribution.checkout_id = revenue.checkout_id

)

select * from final
