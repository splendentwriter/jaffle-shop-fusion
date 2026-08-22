with

source as (

    select * from {{ source('ecom', 'raw_customer_consent') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as consent_id,
        customer_id,

        ---------- text
        consent_type,
        consent_version,

        ---------- timestamps
        granted_at,
        revoked_at,

        ---------- booleans
        revoked_at is null as is_active

    from source

)

select * from renamed
