{% snapshot customer_accounts_snapshot %}

{{
    config(
      unique_key='account_id',
      strategy='timestamp',
      updated_at='updated_at',
    )
}}

-- A snapshot's MERGE requires at most one source row per unique_key; guard
-- against a duplicate account_id the same way products_snapshot does,
-- keeping the most recently updated row if a duplicate ever shows up.
select *
from {{ ref('stg_customer_accounts') }}
qualify row_number() over (
    partition by account_id
    order by updated_at desc
) = 1

{% endsnapshot %}
