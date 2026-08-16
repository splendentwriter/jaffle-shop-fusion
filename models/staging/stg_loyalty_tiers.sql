with

source as (

    select * from {{ source('ecom', 'raw_loyalty_tiers') }}

),

renamed as (

    select

        ----------  ids
        id as tier_id,

        ---------- text
        name as tier_name,
        perk_description,

        ---------- numerics
        min_points_threshold

    from source

)

select * from renamed
