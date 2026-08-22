with

source as (

    select * from {{ source('ecom', 'raw_customer_preferences') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        customer_id,

        ---------- booleans
        marketing_opt_in as is_marketing_opt_in,

        ---------- text
        preferred_channel,
        preferred_language

    from source

)

select * from renamed
