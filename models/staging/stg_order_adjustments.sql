with

source as (

    select * from {{ source('ecom', 'raw_order_adjustments') }}

),

renamed as (

    select

        ----------  ids
        id as order_adjustment_id,
        order_id,

        ---------- text
        adjustment_type,
        reason,

        ---------- numerics
        amount_cents,
        {{ cents_to_dollars('amount_cents') }} as amount,

        ---------- timestamps
        applied_at

    from source

)

select * from renamed
