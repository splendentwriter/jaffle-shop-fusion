with

source as (

    select * from {{ source('ecom', 'raw_review_votes') }}

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
