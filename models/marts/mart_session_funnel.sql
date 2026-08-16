with

sessions as (

    select * from {{ ref('fct_session') }}

),

devices as (

    select * from {{ ref('stg_customer_devices') }}

),

carts as (

    select * from {{ ref('fct_cart') }}

),

checkouts as (

    select * from {{ ref('fct_checkout') }}

),

payments as (

    select
        checkout_id,
        logical_or(attempt_status = 'captured') as is_paid

    from {{ ref('fct_payment') }}
    group by 1

),

final as (

    select

        ----------  ids
        sessions.session_id,

        ---------- text
        sessions.referrer_source,
        coalesce(devices.device_type, 'unknown') as device_type,

        ---------- booleans
        sessions.has_product_view,
        sessions.has_search,
        sessions.has_add_to_cart,
        carts.cart_id is not null as has_cart,
        checkouts.checkout_id is not null as has_checkout,
        coalesce(payments.is_paid, false) as is_paid

    from sessions
    left join devices on sessions.device_id = devices.device_id
    left join carts on sessions.session_id = carts.session_id
    left join checkouts on carts.cart_id = checkouts.cart_id
    left join payments on checkouts.checkout_id = payments.checkout_id

)

select * from final
