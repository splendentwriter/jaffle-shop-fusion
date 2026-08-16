with

source as (

    select * from {{ source('ecom', 'raw_customer_acquisition') }}

),

renamed as (

    select

        ----------  ids
        customer_id,
        nullif(campaign_id, '') as campaign_id,

        ---------- text
        acquisition_channel,

        ---------- timestamps
        acquired_at

    from source

)

select * from renamed
