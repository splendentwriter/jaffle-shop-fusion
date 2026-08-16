with

attribution as (

    select * from {{ ref('fct_campaign_attribution') }}

),

campaigns as (

    select * from {{ ref('stg_campaigns') }}

),

revenue as (

    select checkout_id, gross_revenue_cents from {{ ref('fct_revenue') }}

),

attributed as (

    select
        attribution.campaign_id,
        count(distinct attribution.checkout_id) as attributed_checkouts,
        count(distinct attribution.customer_id) as attributed_customers,
        sum(revenue.gross_revenue_cents) as attributed_revenue_cents

    from attribution
    left join revenue on attribution.checkout_id = revenue.checkout_id
    group by 1

),

final as (

    select

        ----------  ids
        campaigns.campaign_id,

        ---------- text
        campaigns.campaign_name,
        campaigns.campaign_type,

        ---------- numerics
        campaigns.budget,
        coalesce(attributed.attributed_checkouts, 0) as attributed_checkouts,
        coalesce(attributed.attributed_customers, 0) as attributed_customers,
        round(coalesce(attributed.attributed_revenue_cents, 0) / 100.0, 2) as attributed_revenue,
        round(safe_divide(coalesce(attributed.attributed_revenue_cents, 0) / 100.0, campaigns.budget), 4)
            as roas,

        ---------- timestamps
        campaigns.starts_at,
        campaigns.ends_at,

        ---------- booleans
        campaigns.is_active

    from campaigns
    left join attributed on campaigns.campaign_id = attributed.campaign_id

)

select * from final
