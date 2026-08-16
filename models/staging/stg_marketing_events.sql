with

source as (

    select * from {{ source('ecom', 'raw_marketing_events') }}

),

renamed as (

    select

        ----------  ids
        id as marketing_event_id,
        campaign_id,
        customer_id,

        ---------- text
        channel,
        event_type,

        ---------- timestamps
        occurred_at

    from source

)

select * from renamed
