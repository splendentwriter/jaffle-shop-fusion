with

source as (

    select * from {{ source('ecom', 'raw_processing_fee_config') }}

),

renamed as (

    select

        ----------  ids
        id as fee_config_id,

        ---------- text
        provider,

        ---------- numerics
        percentage_fee,
        fixed_fee_cents,

        ---------- timestamps
        effective_from

    from source

)

select * from renamed
