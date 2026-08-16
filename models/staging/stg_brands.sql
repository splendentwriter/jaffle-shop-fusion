with

source as (

    select * from {{ source('ecom', 'raw_brands') }}

),

renamed as (

    select

        ----------  ids
        id as brand_id,

        ---------- text
        brand_name,
        brand_description

    from source

)

select * from renamed
