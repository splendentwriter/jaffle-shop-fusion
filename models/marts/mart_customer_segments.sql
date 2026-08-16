with

customer_360 as (

    select * from {{ ref('mart_customer_360') }}

),

-- quartile thresholds for frequency (order count) and monetary (lifetime
-- spend), computed once across the whole customer base
thresholds as (

    select
        approx_quantiles(count_lifetime_orders, 4)[offset(2)] as frequency_p50,
        approx_quantiles(count_lifetime_orders, 4)[offset(3)] as frequency_p75,
        approx_quantiles(lifetime_spend, 4)[offset(3)] as monetary_p75

    from customer_360

),

final as (

    select

        customer_360.customer_id,
        customer_360.customer_name,
        customer_360.count_lifetime_orders as frequency,
        customer_360.lifetime_spend as monetary,
        customer_360.days_since_last_order as recency_days,

        -- waterfall: first matching rule wins, evaluated most-specific /
        -- most business-critical first (churn risk before upside segments)
        case
            when customer_360.days_since_last_order > 180 then 'Churned'
            when customer_360.days_since_last_order > 90 then 'At Risk'
            when customer_360.count_lifetime_orders = 1 and customer_360.days_since_last_order <= 30
                then 'New'
            when customer_360.count_lifetime_orders >= thresholds.frequency_p75
                and customer_360.lifetime_spend >= thresholds.monetary_p75
                and customer_360.days_since_last_order <= 60
                then 'Champions'
            when customer_360.count_lifetime_orders >= thresholds.frequency_p50
                and customer_360.days_since_last_order <= 90
                then 'Loyal'
            when customer_360.lifetime_spend >= thresholds.monetary_p75 then 'High Value'
            else 'Occasional'
        end as segment

    from customer_360
    cross join thresholds

)

select * from final
