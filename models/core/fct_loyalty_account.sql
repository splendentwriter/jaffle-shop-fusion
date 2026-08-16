with

accounts as (

    select * from {{ ref('stg_loyalty_accounts') }}

),

transactions as (

    select * from {{ ref('stg_loyalty_transactions') }}

),

transaction_summary as (

    select
        loyalty_account_id,
        countif(transaction_type = 'earn') as earn_count,
        sum(case when transaction_type = 'earn' then points else 0 end) as lifetime_points_earned,
        countif(transaction_type = 'redeem') as redemption_count,
        sum(case when transaction_type = 'redeem' then -points else 0 end) as lifetime_points_redeemed,
        sum(case when transaction_type = 'expire' then -points else 0 end) as lifetime_points_expired

    from transactions
    group by 1

),

final as (

    select

        ----------  ids
        accounts.loyalty_account_id,
        accounts.customer_id,
        accounts.tier_id,

        ---------- text
        accounts.status,

        ---------- numerics
        accounts.points_balance,
        coalesce(transaction_summary.earn_count, 0) as earn_count,
        coalesce(transaction_summary.lifetime_points_earned, 0) as lifetime_points_earned,
        coalesce(transaction_summary.redemption_count, 0) as redemption_count,
        coalesce(transaction_summary.lifetime_points_redeemed, 0) as lifetime_points_redeemed,
        coalesce(transaction_summary.lifetime_points_expired, 0) as lifetime_points_expired,

        ---------- timestamps
        accounts.enrolled_at

    from accounts
    left join transaction_summary on accounts.loyalty_account_id = transaction_summary.loyalty_account_id

)

select * from final
