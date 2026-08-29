{% snapshot employees_snapshot %}

{{
    config(
      unique_key='employee_id',
      strategy='check',
      check_cols='all',
    )
}}

-- A snapshot's MERGE requires at most one source row per unique_key; guard
-- against a duplicate employee_id the same way products_snapshot does,
-- keeping a single deterministic row if a duplicate ever shows up.
select *
from {{ ref('stg_employees') }}
qualify row_number() over (
    partition by employee_id
    order by hire_date desc
) = 1

{% endsnapshot %}
