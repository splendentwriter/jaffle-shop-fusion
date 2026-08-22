with

source as (

    select * from {{ source('ecom', 'raw_carts') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as cart_id,
        nullif(customer_id, '') as customer_id,
        session_id,

        ---------- text
        status,

        ---------- timestamps
        created_at,
        updated_at

    from source

)

select * from renamed
