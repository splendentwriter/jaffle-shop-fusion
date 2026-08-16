with

reviews as (

    select * from {{ ref('stg_reviews') }}

),

votes as (

    select * from {{ ref('stg_review_votes') }}

),

vote_summary as (

    select
        review_id,
        countif(vote_type = 'helpful') as helpful_votes,
        countif(vote_type = 'not_helpful') as not_helpful_votes

    from votes
    group by 1

),

moderation as (

    select * from {{ ref('stg_review_moderation_actions') }}

),

response_summary as (

    select
        review_id,
        count(*) as response_count

    from {{ ref('stg_review_responses') }}
    group by 1

),

final as (

    select

        ----------  ids
        reviews.review_id,
        reviews.product_id,
        reviews.customer_id,

        ---------- text
        reviews.title,
        reviews.status,
        moderation.action as moderation_action,
        moderation.reason as moderation_reason,

        ---------- numerics
        reviews.rating,
        coalesce(vote_summary.helpful_votes, 0) as helpful_votes,
        coalesce(vote_summary.not_helpful_votes, 0) as not_helpful_votes,
        coalesce(response_summary.response_count, 0) as response_count,

        ---------- timestamps
        reviews.created_at,

        ---------- booleans
        coalesce(response_summary.response_count, 0) > 0 as has_response

    from reviews
    left join vote_summary on reviews.review_id = vote_summary.review_id
    left join moderation on reviews.review_id = moderation.review_id
    left join response_summary on reviews.review_id = response_summary.review_id

)

select * from final
