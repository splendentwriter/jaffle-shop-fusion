with

redemptions as (

    select * from {{ ref('stg_coupon_redemptions') }}

),

coupons as (

    select * from {{ ref('stg_coupons') }}

),

promotions as (

    select * from {{ ref('stg_promotions') }}

),

final as (

    select

        ----------  ids
        redemptions.redemption_id,
        redemptions.coupon_id,
        redemptions.customer_id,
        redemptions.checkout_id,
        promotions.promotion_id,

        ---------- text
        coupons.code,
        promotions.promotion_name,
        promotions.promotion_type,

        ---------- numerics
        redemptions.discount_amount_cents,
        redemptions.discount_amount,

        ---------- timestamps
        redemptions.redeemed_at

    from redemptions
    left join coupons on redemptions.coupon_id = coupons.coupon_id
    left join promotions on coupons.promotion_id = promotions.promotion_id

)

select * from final
