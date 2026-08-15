{% macro generate_schema_name(custom_schema_name, node) %}

    {% set default_schema = target.schema %}

    {# seeds and staging models are raw/lightly-cleaned data: ingestion layer #}
    {% if node.resource_type == 'seed' or custom_schema_name == 'ingestion' %}
        jaffle_shop_ingestion

    {# marts are business-ready data: analytics layer #}
    {% elif custom_schema_name == 'analytics' %}
        jaffle_shop_analytics

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
