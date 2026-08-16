{% snapshot customer_accounts_snapshot %}

{{
    config(
      unique_key='account_id',
      strategy='timestamp',
      updated_at='updated_at',
    )
}}

select * from {{ ref('stg_customer_accounts') }}

{% endsnapshot %}
