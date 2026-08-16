with

source as (

    select * from {{ source('ecom', 'raw_supplier_products') }}

),

renamed as (

    select

        ----------  ids
        id as supplier_product_id,
        supplier_id,
        sku as product_id,

        ---------- text
        supplier_sku,

        ---------- numerics
        unit_cost_cents,
        {{ cents_to_dollars('unit_cost_cents') }} as unit_cost,
        lead_time_days

    from source

)

select * from renamed
