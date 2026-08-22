with

source as (

    select * from {{ source('ecom', 'raw_return_inspections') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as return_inspection_id,
        return_item_id,

        ---------- text
        inspection_result,
        inspector_notes,

        ---------- timestamps
        inspected_at

    from source

)

select * from renamed
