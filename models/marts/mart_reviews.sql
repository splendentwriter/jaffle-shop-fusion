with

reviews as (

    select * from {{ ref('fct_review') }}

),

products as (

    select * from {{ ref('dim_product') }}
    where is_current

),

final as (

    select

        ----------  ids
        reviews.review_id,
        reviews.product_id,
        reviews.customer_id,

        ---------- text
        products.product_name,
        reviews.title,
        reviews.status,
        reviews.moderation_action,
        reviews.moderation_reason,

        ---------- numerics
        reviews.rating,
        reviews.helpful_votes,
        reviews.not_helpful_votes,
        reviews.response_count,

        ---------- timestamps
        reviews.created_at,

        ---------- booleans
        reviews.has_response,
        reviews.rating <= 2 as is_negative

    from reviews
    left join products on reviews.product_id = products.product_id

)

select * from final
