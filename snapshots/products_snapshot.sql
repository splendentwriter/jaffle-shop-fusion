{% snapshot products_snapshot %}

{{
    config(
      unique_key='product_id',
      strategy='check',
      check_cols='all',
    )
}}

-- product_id (sku) isn't guaranteed unique at the source: a rolling Cloud
-- Run redeploy of generate_stream_data.py can let two instances briefly
-- allocate the same next SKU before either insert is visible to the
-- other's sequence query. A snapshot's MERGE requires at most one source
-- row per unique_key, so keep one deterministic row per product_id here
-- rather than letting the whole run fail on a handful of collided SKUs.
select *
from {{ ref('stg_products') }}
qualify row_number() over (
    partition by product_id
    order by product_name, product_type, product_price
) = 1

{% endsnapshot %}
