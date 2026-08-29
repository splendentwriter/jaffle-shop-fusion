{% snapshot support_tickets_snapshot %}

{{
    config(
      unique_key='ticket_id',
      strategy='check',
      check_cols='all',
    )
}}

-- A snapshot's MERGE requires at most one source row per unique_key; guard
-- against a duplicate ticket_id the same way products_snapshot does,
-- keeping a single deterministic row if a duplicate ever shows up.
select *
from {{ ref('stg_support_tickets') }}
qualify row_number() over (
    partition by ticket_id
    order by created_at desc
) = 1

{% endsnapshot %}
