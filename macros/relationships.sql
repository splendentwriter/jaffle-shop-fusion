{% test relationships(model, column_name, to, field) %}

    {#- every source table is independently row-limited via limit_in_dev()
       outside of prod, so foreign keys don't line up across the sampled
       rows and this test produces false positives. Downgrade to a warning
       there; every other test type is unaffected by the sampling and still
       enforces at full severity. -#}
    {{ config(severity='warn' if target.name != 'prod' else 'error') }}

    {% set macro = adapter.dispatch('test_relationships', 'dbt') %}
    {{ macro(model, column_name, to, field) }}

{% endtest %}
