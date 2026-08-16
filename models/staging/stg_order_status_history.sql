with

source as (

    select * from {{ source('ecom', 'raw_order_status_history') }}

),

renamed as (

    select

        ----------  ids
        id as order_status_id,
        order_id,

        ---------- text
        status,

        ---------- timestamps
        occurred_at

    from source

)

select * from renamed
