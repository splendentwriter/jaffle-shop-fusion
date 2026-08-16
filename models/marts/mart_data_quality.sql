with

test_results as (

    select * from {{ source('elementary', 'elementary_test_results') }}

),

models as (

    select * from {{ source('elementary', 'dbt_models') }}
    where package_name = 'jaffle_shop'

),

-- one row per test: only the most recent result, so this mart reflects
-- current data quality rather than accumulating every historical run
latest as (

    select
        test_results.*,
        row_number() over (
            partition by test_results.test_unique_id
            order by test_results.created_at desc
        ) as recency_rank

    from test_results
    inner join models on test_results.model_unique_id = models.unique_id

),

final as (

    select

        ----------  ids
        test_unique_id,
        model_unique_id,

        ---------- text
        test_name,
        test_type,
        test_sub_type,
        table_name,
        column_name,
        upper(severity) as severity,
        status,
        test_results_description,

        ---------- numerics
        coalesce(failures, 0) as failures,
        coalesce(failed_row_count, 0) as failed_row_count,

        ---------- timestamps
        created_at as last_run_at,

        ---------- booleans
        status = 'fail' as is_failing,
        status = 'warn' as is_warning

    from latest
    where recency_rank = 1

)

select * from final
