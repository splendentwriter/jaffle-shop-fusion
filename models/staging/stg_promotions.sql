with

source as (

    select * from {{ source('ecom', 'raw_promotions') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as promotion_id,

        ---------- text
        name as promotion_name,
        description,
        promotion_type,

        ---------- numerics
        discount_value,
        min_order_value_cents,
        max_discount_cents,

        ---------- timestamps
        starts_at,
        ends_at,

        ---------- booleans
        is_active

    from source

)

select * from renamed
