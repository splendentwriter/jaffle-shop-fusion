with

addresses as (

    select * from {{ ref('stg_customer_addresses') }}

),

-- upstream ingestion occasionally double-inserts the same address; collapse
-- exact business-key duplicates down to a single row
deduplicated as (

    select
        *,
        row_number() over (
            partition by customer_id, address_type, address_line1
            order by address_id
        ) as dedup_row_num

    from addresses

),

final as (

    select
        address_id,
        customer_id,
        address_type,
        address_line1,
        city,
        region,
        postal_code,
        country_code,
        is_default

    from deduplicated
    where dedup_row_num = 1

)

select * from final
