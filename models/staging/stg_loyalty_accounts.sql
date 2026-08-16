with

source as (

    select * from {{ source('ecom', 'raw_loyalty_accounts') }}

),

renamed as (

    select

        ----------  ids
        id as loyalty_account_id,
        customer_id,
        tier_id,

        ---------- text
        status,

        ---------- numerics
        points_balance,

        ---------- timestamps
        enrolled_at

    from source

)

select * from renamed
