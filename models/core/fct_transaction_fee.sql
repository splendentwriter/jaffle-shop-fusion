with

captures as (

    select * from {{ ref('stg_captures') }}

),

-- single active fee config today; cross join is safe as long as that stays
-- true (would need a date-effective join if a second provider is added)
fee_config as (

    select * from {{ ref('stg_processing_fee_config') }}
    where provider = 'platform'

),

final as (

    select

        ----------  ids
        captures.capture_id,
        captures.authorization_id,

        ---------- numerics
        captures.amount_cents as captured_amount_cents,
        round(captures.amount_cents * fee_config.percentage_fee) + fee_config.fixed_fee_cents as fee_cents,
        captures.amount_cents
            - (round(captures.amount_cents * fee_config.percentage_fee) + fee_config.fixed_fee_cents)
            as net_amount_cents,

        ---------- timestamps
        captures.captured_at

    from captures
    cross join fee_config

)

select * from final
