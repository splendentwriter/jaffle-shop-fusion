{% macro generate_schema_name(custom_schema_name, node) %}

    {% set default_schema = target.schema %}

    {# fixed layer datasets: raw seeds, lightly-cleaned staging, business-ready analytics, elementary tracking #}
    {% set layer_datasets = {
        "raw": "jaffle_shop_raw",
        "ingestion": "jaffle_shop_ingestion",
        "analytics": "jaffle_shop_analytics",
        "elementary": "jaffle_shop_elementary",
    } %}

    {% if custom_schema_name in layer_datasets %}
        {{ layer_datasets[custom_schema_name] }}

    {# non-specified schemas go to the default target schema #}
    {% elif custom_schema_name is none %}
        {{ default_schema }}


    {# specified custom schema names go to the schema name prepended with the the default schema name in prod (as this is an example project we want the schemas clearly labeled) #}
    {% elif target.name == 'prod' %}
        {{ default_schema }}_{{ custom_schema_name | trim }}

    {# specified custom schemas go to the default target schema for non-prod targets #}
    {% else %}
        {{ default_schema }}
    {% endif %}

{% endmacro %}
