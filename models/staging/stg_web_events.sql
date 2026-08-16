with

source as (

    select * from {{ source('ecom', 'raw_web_events') }}

),

renamed as (

    select

        ----------  ids
        id as event_id,
        session_id,
        nullif(product_sku, '') as product_id,

        ---------- text
        event_type,
        page_url,
        nullif(search_query, '') as search_query,

        ---------- timestamps
        occurred_at

    from source

)

select * from renamed
