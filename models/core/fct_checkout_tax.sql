with

checkouts as (

    select * from {{ ref('stg_checkouts') }}

),

tax_rates as (

    select * from {{ ref('stg_tax_rates') }}

),

items as (

    select * from {{ ref('stg_checkout_items') }}

),

item_summary as (

    select
        checkout_id,
        sum(quantity * unit_price_cents) as items_subtotal_cents

    from items
    group by 1

),

final as (

    select

        ----------  ids
        checkouts.checkout_id,

        ---------- text
        checkouts.shipping_region,

        ---------- numerics
        tax_rates.tax_rate,
        coalesce(item_summary.items_subtotal_cents, 0) as items_subtotal_cents,
        round(coalesce(item_summary.items_subtotal_cents, 0) * coalesce(tax_rates.tax_rate, 0))
            as tax_amount_cents

    from checkouts
    left join tax_rates on checkouts.shipping_region = tax_rates.region
    left join item_summary on checkouts.checkout_id = item_summary.checkout_id

)

select * from final
