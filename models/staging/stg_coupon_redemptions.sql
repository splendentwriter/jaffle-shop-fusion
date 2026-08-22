with

source as (

    select * from {{ source('ecom', 'raw_coupon_redemptions') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as redemption_id,
        coupon_id,
        nullif(customer_id, '') as customer_id,
        checkout_id,

        ---------- numerics
        discount_amount_cents,
        {{ cents_to_dollars('discount_amount_cents') }} as discount_amount,

        ---------- timestamps
        redeemed_at

    from source

)

select * from renamed
