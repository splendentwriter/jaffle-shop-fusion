with

source as (

    select * from {{ source('ecom', 'raw_campaign_channels') }}

),

renamed as (

    select

        ----------  ids
        id as campaign_channel_id,
        campaign_id,

        ---------- text
        channel

    from source

)

select * from renamed
