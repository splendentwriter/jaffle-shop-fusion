with

source as (

    select * from {{ source('ecom', 'raw_carriers') }}

),

renamed as (

    select

        ----------  ids
        id as carrier_id,

        ---------- text
        name as carrier_name,
        tracking_url_template

    from source

)

select * from renamed
