with

customers as (

    select * from {{ ref('stg_customers') }}

),

account_history as (

    select * from {{ ref('customer_accounts_snapshot') }}

),

final as (

    select

        ----------  ids
        account_history.account_id,
        customers.customer_id,

        ---------- text
        customers.customer_name,
        account_history.account_email,
        account_history.account_status,
        account_history.account_type,

        ---------- scd2 tracking
        account_history.dbt_valid_from as valid_from,
        account_history.dbt_valid_to as valid_to,
        account_history.dbt_valid_to is null as is_current

    from account_history
    inner join customers on account_history.customer_id = customers.customer_id

)

select * from final
