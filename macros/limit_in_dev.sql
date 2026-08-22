{% macro limit_in_dev(row_limit=1000) %}
    {#- caps rows pulled from sources for any non-prod target, so CI/dev builds
       don't have to churn through full production data volumes -#}
    {%- if target.name != 'prod' -%}
    limit {{ row_limit }}
    {%- endif -%}
{% endmacro %}
