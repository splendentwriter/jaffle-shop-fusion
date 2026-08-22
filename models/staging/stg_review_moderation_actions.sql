with

source as (

    select * from {{ source('ecom', 'raw_review_moderation_actions') }}
    {{ limit_in_dev() }}

),

renamed as (

    select

        ----------  ids
        id as moderation_action_id,
        review_id,

        ---------- text
        action,
        nullif(reason, '') as reason,

        ---------- timestamps
        moderated_at

    from source

)

select * from renamed
