with

acquisition as (

    select * from {{ ref('stg_customer_acquisition') }}

),

customer_360 as (

    select * from {{ ref('mart_customer_360') }}

),

final as (

    select
        acquisition.acquisition_channel,
        count(distinct acquisition.customer_id) as customer_count,
        round(sum(customer_360.lifetime_spend), 2) as total_revenue,
        round(safe_divide(sum(customer_360.lifetime_spend), count(distinct acquisition.customer_id)), 2)
            as avg_lifetime_value

    from acquisition
    left join customer_360 on acquisition.customer_id = customer_360.customer_id
    group by 1

)

select * from final
order by total_revenue desc
