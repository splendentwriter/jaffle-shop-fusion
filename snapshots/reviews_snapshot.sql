{% snapshot reviews_snapshot %}

{{
    config(
      unique_key='review_id',
      strategy='check',
      check_cols='all',
    )
}}

-- A snapshot's MERGE requires at most one source row per unique_key; guard
-- against a duplicate review_id the same way products_snapshot does,
-- keeping a single deterministic row if a duplicate ever shows up.
select *
from {{ ref('stg_reviews') }}
qualify row_number() over (
    partition by review_id
    order by created_at desc
) = 1

{% endsnapshot %}
