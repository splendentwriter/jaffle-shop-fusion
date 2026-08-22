with

source as (

    select * from {{ source('ecom', 'raw_reviews') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as review_id,
        product_id,
        customer_id,

        ---------- text
        title,
        body,
        status,

        ---------- numerics
        rating,

        ---------- timestamps
        created_at

    from source

)

select * from renamed
