with

source as (

    select * from {{ source('ecom', 'raw_checkout_failures') }}

),

renamed as (

    select

        ----------  ids
        id as checkout_failure_id,
        checkout_id,

        ---------- text
        failure_reason,

        ---------- timestamps
        occurred_at,

        ---------- booleans
        is_retried

    from source

)

select * from renamed
