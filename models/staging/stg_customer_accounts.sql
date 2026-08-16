with

source as (

    select * from {{ source('ecom', 'raw_customer_accounts') }}

),

renamed as (

    select

        ----------  ids
        id as account_id,
        nullif(customer_id, '') as customer_id,

        ---------- text
        email as account_email,
        account_status,
        account_type,

        ---------- timestamps
        created_at,
        updated_at

    from source

)

select * from renamed
