with

source as (

    select * from {{ source('ecom', 'raw_warehouses') }}
    {{ limit_in_dev() }}

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
