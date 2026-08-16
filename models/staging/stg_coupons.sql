with

source as (

    select * from {{ source('ecom', 'raw_coupons') }}

),

renamed as (

    select

        ----------  ids
        id as coupon_id,
        promotion_id,

        ---------- text
        code,

        ---------- numerics
        max_redemptions,
        max_redemptions_per_customer,

        ---------- booleans
        is_active

    from source

)

select * from renamed
