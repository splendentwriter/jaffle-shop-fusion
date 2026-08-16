with

source as (

    select * from {{ source('ecom', 'raw_loyalty_transactions') }}

),

renamed as (

    select

        ----------  ids
        id as loyalty_transaction_id,
        loyalty_account_id,
        nullif(reward_id, '') as reward_id,
        nullif(related_checkout_id, '') as related_checkout_id,

        ---------- text
        transaction_type,

        ---------- numerics
        points,

        ---------- timestamps
        occurred_at

    from source

)

select * from renamed
