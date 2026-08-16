with

reviews as (

    select * from {{ ref('stg_reviews') }}
    where status = 'published'

),

final as (

    select
        product_id,
        count(*) as published_review_count,
        round(avg(rating), 2) as average_rating,
        countif(rating >= 4) as positive_review_count,
        countif(rating <= 2) as negative_review_count

    from reviews
    group by 1

)

select * from final
