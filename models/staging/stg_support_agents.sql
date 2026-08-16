with

source as (

    select * from {{ source('ecom', 'raw_support_agents') }}

),

renamed as (

    select

        ----------  ids
        id as agent_id,

        ---------- text
        name as agent_name,
        email as agent_email,
        team,

        ---------- booleans
        is_active

    from source

)

select * from renamed
