with

source as (

    select * from {{ source('ecom', 'raw_suppliers') }}

),

renamed as (

    select

        ----------  ids
        id as supplier_id,

        ---------- text
        name as supplier_name,
        contact_email,

        ---------- booleans
        is_active

    from source

)

select * from renamed
