with

redemptions as (

    select * from {{ ref('fct_coupon_redemption') }}

),

revenue as (

    select checkout_id, gross_revenue_cents from {{ ref('fct_revenue') }}

),

final as (

    select

        ----------  ids
        redemptions.promotion_id,

        ---------- text
        redemptions.promotion_name,
        redemptions.promotion_type,

        ---------- numerics
        count(*) as redemption_count,
        count(distinct redemptions.customer_id) as redeeming_customers,
        round(sum(redemptions.discount_amount), 2) as total_discount_given,
        round(sum(coalesce(revenue.gross_revenue_cents, 0)) / 100.0, 2) as attributed_revenue

    from redemptions
    left join revenue on redemptions.checkout_id = revenue.checkout_id
    group by 1, 2, 3

)

select * from final
