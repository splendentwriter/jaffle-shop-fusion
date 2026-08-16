with

run_results as (

    select * from {{ source('elementary', 'dbt_run_results') }}
    where resource_type = 'model'

),

models as (

    select * from {{ source('elementary', 'dbt_models') }}
    where package_name = 'jaffle_shop'

),

final as (

    select

        ----------  ids
        run_results.model_execution_id,
        run_results.unique_id,
        run_results.invocation_id,

        ---------- text
        run_results.name,
        models.schema_name,
        run_results.materialization,
        run_results.status,

        ---------- numerics
        round(run_results.execution_time, 2) as execution_time_seconds,
        coalesce(run_results.rows_affected, 0) as rows_affected,

        ---------- timestamps
        run_results.created_at,

        ---------- booleans
        run_results.status = 'success' as is_successful,
        run_results.status = 'error' as is_error

    from run_results
    inner join models on run_results.unique_id = models.unique_id

)

select * from final
