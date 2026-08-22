with

source as (

    select * from {{ source('ecom', 'raw_rewards') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as reward_id,

        ---------- text
        name as reward_name,
        reward_type,

        ---------- numerics
        points_cost

    from source

)

select * from renamed
