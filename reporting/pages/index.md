---
title: Jaffle Shop — Business Overview
---

<!--
Each block below is a thin pass-through over a query that actually runs
against BigQuery: the real SQL lives in sources/jaffle_shop/<name>.sql and
gets executed there during `evidence sources`, then cached locally. Pages
query that local cache via `sourcename.queryname` — they can't embed
BigQuery-dialect SQL (backtick-quoted identifiers, etc.) directly, since
page queries run against the local cache engine, not BigQuery itself.
-->

```sql kpi_summary
select * from jaffle_shop.kpi_summary
```

```sql revenue_trend
select * from jaffle_shop.revenue_trend
```

```sql checkout_funnel
select * from jaffle_shop.checkout_funnel
```

```sql payment_performance
select * from jaffle_shop.payment_performance
```

```sql revenue_breakdown
select * from jaffle_shop.revenue_breakdown
```

```sql top_products
select * from jaffle_shop.top_products
```

```sql fulfillment_performance
select * from jaffle_shop.fulfillment_performance
```

```sql shipping_performance
select * from jaffle_shop.shipping_performance
```

## Headline metrics

<BigValue
    data={kpi_summary}
    value=total_revenue
    fmt=usd
    title="Total Revenue"
/>

<BigValue
    data={kpi_summary}
    value=total_orders
    fmt=num0
    title="Total Orders"
/>

<BigValue
    data={kpi_summary}
    value=total_customers
    fmt=num0
    title="Total Customers"
/>

<BigValue
    data={kpi_summary}
    value=avg_order_value
    fmt=usd2
    title="Avg Order Value"
/>

## Revenue trend

<LineChart
    data={revenue_trend}
    x=month
    y=revenue
    title="Monthly Revenue"
    yFmt=usd0
/>

<DataTable data={revenue_trend}>
    <Column id=month fmt="mmm yyyy"/>
    <Column id=revenue fmt=usd0/>
    <Column id=orders/>
</DataTable>

## Checkout & payment funnel

Covers the cart → checkout → payment funnel built out on top of this session's
web-behaviour data (a separate, smaller-scale funnel from the historical
orders above — see the platform's `CONVENTIONS.md` for why the two aren't
merged).

<BigValue data={checkout_funnel} value=checkouts_started title="Checkouts Started"/>
<BigValue data={checkout_funnel} value=checkouts_completed title="Completed"/>
<BigValue data={checkout_funnel} value=checkouts_failed title="Failed"/>
<BigValue data={checkout_funnel} value=checkouts_abandoned title="Abandoned"/>

<BigValue data={payment_performance} value=captured title="Payments Captured"/>
<BigValue data={payment_performance} value=total_captured fmt=usd title="Captured Amount"/>
<BigValue data={payment_performance} value=total_refunded fmt=usd title="Refunded Amount"/>

### Revenue breakdown (this funnel)

<DataTable data={revenue_breakdown}>
    <Column id=gross_revenue fmt=usd/>
    <Column id=net_revenue fmt=usd/>
    <Column id=total_discounts fmt=usd/>
    <Column id=total_processing_fees fmt=usd/>
    <Column id=total_refunds fmt=usd/>
</DataTable>

Gross revenue excludes sales tax collected on behalf of the tax authority;
net revenue further nets off payment processing fees.

## Top products

<DataTable data={top_products}>
    <Column id=product_name title="Product"/>
    <Column id=orders/>
    <Column id=revenue fmt=usd/>
</DataTable>

## Fulfillment & shipping

<BigValue data={fulfillment_performance} value=fulfillment_orders title="Fulfillment Orders"/>
<BigValue data={fulfillment_performance} value=shipped title="Shipped"/>
<BigValue data={fulfillment_performance} value=avg_hours_to_ship title="Avg Hours to Ship" fmt=num1/>

<BigValue data={shipping_performance} value=shipments title="Shipments"/>
<BigValue data={shipping_performance} value=on_time_delivery_pct title="On-Time Delivery %" fmt=num1/>
<BigValue data={shipping_performance} value=avg_hours_to_deliver title="Avg Hours to Deliver" fmt=num1/>
