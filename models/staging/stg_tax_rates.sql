with

source as (

    select * from {{ source('ecom', 'raw_tax_rates') }}

),

renamed as (

    select

        ----------  ids
        id as tax_rate_id,

        ---------- text
        region,

        ---------- numerics
        tax_rate,

        ---------- timestamps
        effective_from

    from source

)

select * from renamed
