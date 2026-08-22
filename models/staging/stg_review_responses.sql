with

source as (

    select * from {{ source('ecom', 'raw_review_responses') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as review_response_id,
        review_id,

        ---------- text
        response_body,
        responder_role,

        ---------- timestamps
        responded_at

    from source

)

select * from renamed
