with

source as (

    select * from {{ source('ecom', 'raw_customer_addresses') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as address_id,
        customer_id,

        ---------- text
        address_type,
        line1 as address_line1,
        city,
        region,
        nullif(postal_code, '') as postal_code,
        country_code,

        ---------- booleans
        is_default

    from source

)

select * from renamed
