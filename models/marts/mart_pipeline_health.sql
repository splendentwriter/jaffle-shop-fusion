with

run_results as (

    select * from {{ source('elementary', 'dbt_run_results') }}

),

invocations as (

    select * from {{ source('elementary', 'dbt_invocations') }}

),

per_invocation as (

    select
        invocation_id,

        countif(resource_type = 'model') as model_count,
        countif(resource_type = 'model' and status = 'success') as model_success_count,
        countif(resource_type = 'model' and status = 'error') as model_error_count,
        countif(resource_type in ('model', 'snapshot', 'seed') and status = 'error') as node_error_count,

        countif(resource_type = 'test') as test_count,
        countif(resource_type = 'test' and status = 'pass') as test_pass_count,
        countif(resource_type = 'test' and status = 'fail') as test_fail_count,
        countif(resource_type = 'test' and status = 'warn') as test_warn_count,

        sum(execution_time) as total_execution_time_seconds,
        max(created_at) as finished_at

    from run_results
    group by 1

),

final as (

    select

        ----------  ids
        invocations.invocation_id,

        ---------- text
        invocations.command,
        invocations.target_name,
        invocations.dbt_version,

        ---------- numerics
        coalesce(per_invocation.model_count, 0) as model_count,
        coalesce(per_invocation.model_success_count, 0) as model_success_count,
        coalesce(per_invocation.model_error_count, 0) as model_error_count,
        coalesce(per_invocation.test_count, 0) as test_count,
        coalesce(per_invocation.test_pass_count, 0) as test_pass_count,
        coalesce(per_invocation.test_fail_count, 0) as test_fail_count,
        coalesce(per_invocation.test_warn_count, 0) as test_warn_count,
        round(coalesce(per_invocation.total_execution_time_seconds, 0), 2) as total_execution_time_seconds,

        ---------- timestamps
        invocations.created_at as started_at,
        per_invocation.finished_at,

        ---------- booleans
        coalesce(per_invocation.node_error_count, 0) = 0 as is_successful

    from invocations
    left join per_invocation on invocations.invocation_id = per_invocation.invocation_id

)

select * from final
