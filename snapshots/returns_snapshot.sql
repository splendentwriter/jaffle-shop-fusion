{% snapshot returns_snapshot %}

{{
    config(
      unique_key='return_id',
      strategy='check',
      check_cols='all',
    )
}}

-- A snapshot's MERGE requires at most one source row per unique_key; guard
-- against a duplicate return_id the same way products_snapshot does,
-- keeping a single deterministic row if a duplicate ever shows up.
select *
from {{ ref('stg_returns') }}
qualify row_number() over (
    partition by return_id
    order by requested_at desc
) = 1

{% endsnapshot %}
