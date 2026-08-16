with

source as (

    select * from {{ source('ecom', 'raw_campaigns') }}

),

renamed as (

    select

        ----------  ids
        id as campaign_id,

        ---------- text
        name as campaign_name,
        campaign_type,

        ---------- numerics
        budget_cents,
        {{ cents_to_dollars('budget_cents') }} as budget,

        ---------- timestamps
        starts_at,
        ends_at,

        ---------- booleans
        is_active

    from source

)

select * from renamed
