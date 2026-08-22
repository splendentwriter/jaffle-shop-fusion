with

source as (

    select * from {{ source('ecom', 'raw_checkouts') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as checkout_id,
        cart_id,
        nullif(customer_id, '') as customer_id,

        ---------- text
        status,
        shipping_method,
        shipping_line1,
        shipping_city,
        shipping_region,
        shipping_postal_code,
        shipping_country_code,

        ---------- numerics
        shipping_cost_cents,
        {{ cents_to_dollars('shipping_cost_cents') }} as shipping_cost,

        ---------- timestamps
        started_at,
        completed_at

    from source

)

select * from renamed
