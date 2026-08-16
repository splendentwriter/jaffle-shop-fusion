with

source as (

    select * from {{ source('ecom', 'raw_warehouses') }}

),

renamed as (

    select

        ----------  ids
        id as warehouse_id,

        ---------- text
        name as warehouse_name,
        region,

        ---------- booleans
        is_active

    from source

)

select * from renamed
