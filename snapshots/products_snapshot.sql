{% snapshot products_snapshot %}

{{
    config(
      unique_key='product_id',
      strategy='check',
      check_cols='all',
    )
}}

select * from {{ ref('stg_products') }}

{% endsnapshot %}
