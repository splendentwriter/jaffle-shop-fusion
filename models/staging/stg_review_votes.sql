with

source as (

    select * from {{ source('ecom', 'raw_review_votes') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as review_vote_id,
        review_id,
        customer_id,

        ---------- text
        vote_type

    from source

)

select * from renamed
