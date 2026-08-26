{% snapshot inventory_levels_snapshot %}

{{
    config(
      unique_key=['warehouse_id', 'product_id'],
      strategy='check',
      check_cols=['quantity_on_hand', 'reorder_point'],
    )
}}

-- A snapshot's MERGE requires at most one source row per unique_key; guard
-- against a duplicate (warehouse_id, product_id) pair the same way
-- products_snapshot does, keeping the most recently updated row.
select *
from {{ ref('stg_inventory_levels') }}
qualify row_number() over (
    partition by warehouse_id, product_id
    order by updated_at desc
) = 1

{% endsnapshot %}
