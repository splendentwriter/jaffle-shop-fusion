with

adjustments as (

    select * from {{ ref('stg_order_adjustments') }}

),

final as (

    select
        order_id,
        count(*) as adjustment_count,
        sum(amount_cents) as total_adjustment_cents,
        sum(amount) as total_adjustment,
        countif(adjustment_type in ('discount', 'goodwill_credit')) as credit_count,
        countif(adjustment_type in ('price_correction', 'tax_correction')) as correction_count

    from adjustments
    group by order_id

)

select * from final
