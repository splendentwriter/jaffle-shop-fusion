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
        -- cast to timestamp (not datetime) so this matches the type dbt's
        -- snapshot machinery uses internally for dbt_valid_from/dbt_valid_to
        cast(created_at as timestamp) as created_at,
        cast(updated_at as timestamp) as updated_at

    from source

)

select * from renamed
