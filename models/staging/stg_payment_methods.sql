with

source as (

    select * from {{ source('ecom', 'raw_payment_methods') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as payment_method_id,
        customer_id,

        ---------- text
        method_type,
        nullif(card_brand, '') as card_brand,
        last4,
        expiry_month,
        expiry_year,

        ---------- timestamps
        created_at,

        ---------- booleans
        is_default

    from source

)

select * from renamed
