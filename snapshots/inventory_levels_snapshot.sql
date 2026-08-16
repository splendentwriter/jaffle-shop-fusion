{% snapshot inventory_levels_snapshot %}

{{
    config(
      unique_key=['warehouse_id', 'product_id'],
      strategy='check',
      check_cols=['quantity_on_hand', 'reorder_point'],
    )
}}

select * from {{ ref('stg_inventory_levels') }}

{% endsnapshot %}
