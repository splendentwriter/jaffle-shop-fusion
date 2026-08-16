with

customers as (

    select * from {{ ref('customers') }}

),

-- dim_customer's grain is per-account (a customer can have >1 account);
-- pick one canonical current account per customer, deterministically
current_account as (

    select
        *,
        row_number() over (partition by customer_id order by account_id) as account_rank

    from {{ ref('dim_customer') }}
    where is_current

),

acquisition as (

    select * from {{ ref('stg_customer_acquisition') }}

),

support_summary as (

    select
        customer_id,
        count(*) as support_ticket_count

    from {{ ref('fct_support_ticket') }}
    group by 1

),

review_summary as (

    select
        customer_id,
        count(*) as review_count,
        round(avg(rating), 2) as avg_rating_given

    from {{ ref('fct_review') }}
    group by 1

),

final as (

    select

        ----------  ids
        customers.customer_id,

        ---------- text
        customers.customer_name,
        current_account.account_status,
        current_account.account_type,
        acquisition.acquisition_channel,
        customers.customer_type,

        ---------- numerics
        customers.count_lifetime_orders,
        customers.lifetime_spend,
        round(safe_divide(customers.lifetime_spend, customers.count_lifetime_orders), 2)
            as avg_order_value,
        coalesce(support_summary.support_ticket_count, 0) as support_ticket_count,
        coalesce(review_summary.review_count, 0) as review_count,
        review_summary.avg_rating_given,
        date_diff(current_date(), date(customers.last_ordered_at), day) as days_since_last_order,

        ---------- timestamps
        customers.first_ordered_at,
        customers.last_ordered_at

    from customers
    left join current_account on customers.customer_id = current_account.customer_id and current_account.account_rank = 1
    left join acquisition on customers.customer_id = acquisition.customer_id
    left join support_summary on customers.customer_id = support_summary.customer_id
    left join review_summary on customers.customer_id = review_summary.customer_id

)

select * from final
