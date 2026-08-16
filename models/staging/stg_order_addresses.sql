with

source as (

    select * from {{ source('ecom', 'raw_order_addresses') }}

),

renamed as (

    select

        ----------  ids
        id as order_address_id,
        order_id,

        ---------- text
        address_type,
        line1 as address_line1,
        city,
        region,
        postal_code,
        country_code

    from source

)

select * from renamed
