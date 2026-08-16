"""Jaffle Shop — Analytics Command Center application shell.

Defines the business-operation navigation (Executive, Commerce, Customers,
Products, Operations, Finance, Marketing, Customer Experience, Data
Platform) and hands off to the selected page. No business logic lives
here — see CONVENTIONS.md in the repo root: dbt owns business logic,
Streamlit only presents it.
"""

import streamlit as st

from utils.config import APP_ICON, APP_TITLE

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

# Center the top-position nav pills within the header toolbar. The toolbar
# row is [empty spacer, nav pills, status/Deploy/menu actions] all packed
# left by default with no room for justify-content alone to matter, so this
# uses the classic flex trick: grow the spacer and the actions block by
# equal amounts, which centers the nav pills between them while keeping the
# Deploy/menu controls flush right. Selectors are built from stable
# data-testid attributes plus structural pseudo-classes (:has, :empty,
# :last-child), not Streamlit's emotion-hash classnames, which change
# across builds.
st.markdown(
    """
    <style>
    [data-testid="stToolbar"] > div:has([data-testid="stTopNavSection"]) {
        flex: 1 1 auto;
        display: flex;
        width: 100%;
    }
    [data-testid="stToolbar"] > div:has([data-testid="stTopNavSection"]) > div:empty:first-child {
        flex: 1 1 0;
    }
    [data-testid="stToolbar"] > div:has([data-testid="stTopNavSection"]) > *:last-child {
        flex: 1 1 0;
        display: flex;
        justify-content: flex-end;
    }
    /* The nav pill row (rc-overflow, an ant-design-family component) ships
       its own width: 100% rule that greedily fills all space handed to it,
       which is what makes it responsively collapse extra sections into a
       "more" dropdown. That greediness defeats the symmetric-spacer trick
       above, so pin it to its actual content width (!important needed to
       beat that rule's classname-based specificity). */
    [data-testid="stToolbar"] .rc-overflow {
        width: fit-content !important;
        flex: 0 1 auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

executive_command_center = st.Page(
    "pages/executive/command_center.py",
    title="Command Center",
    icon="🏠",
    url_path="executive-command-center",
    default=True,
)
executive_overview = st.Page(
    "pages/executive/overview.py", title="Overview", icon="📊", url_path="executive-overview"
)

sales_overview = st.Page(
    "pages/commerce/sales_overview.py", title="Sales Overview", icon="💰", url_path="commerce-sales"
)
sales_funnel = st.Page(
    "pages/commerce/sales_funnel.py", title="Sales Funnel", icon="🔻", url_path="commerce-funnel"
)
orders = st.Page("pages/commerce/orders.py", title="Orders", icon="📋", url_path="commerce-orders")
promotions = st.Page(
    "pages/commerce/promotions.py", title="Promotions", icon="🏷️", url_path="commerce-promotions"
)

customer_360 = st.Page(
    "pages/customers/customer_360.py", title="Customer 360", icon="👥", url_path="customers-360"
)
acquisition = st.Page(
    "pages/customers/acquisition.py",
    title="Customer Acquisition",
    icon="📥",
    url_path="customers-acquisition",
)
retention = st.Page(
    "pages/customers/retention.py", title="Customer Retention", icon="🔁", url_path="customers-retention"
)

product_performance = st.Page(
    "pages/products/performance.py",
    title="Product Performance",
    icon="🛍️",
    url_path="products-performance",
)
catalogue_health = st.Page(
    "pages/products/catalogue_health.py",
    title="Catalogue Health",
    icon="📋",
    url_path="products-catalogue-health",
)

inventory = st.Page(
    "pages/operations/inventory.py", title="Inventory", icon="📦", url_path="operations-inventory"
)
fulfillment = st.Page(
    "pages/operations/fulfillment.py", title="Fulfillment", icon="🏭", url_path="operations-fulfillment"
)
shipping = st.Page(
    "pages/operations/shipping.py",
    title="Shipping & Delivery",
    icon="🚚",
    url_path="operations-shipping",
)

payments = st.Page("pages/finance/payments.py", title="Payments", icon="💳", url_path="finance-payments")
revenue_profitability = st.Page(
    "pages/finance/revenue_profitability.py",
    title="Revenue & Profitability",
    icon="💰",
    url_path="finance-profitability",
)
returns_refunds = st.Page(
    "pages/finance/returns_refunds.py",
    title="Returns & Refunds",
    icon="↩️",
    url_path="finance-returns-refunds",
)
reconciliation = st.Page(
    "pages/finance/reconciliation.py",
    title="Reconciliation",
    icon="🧾",
    url_path="finance-reconciliation",
)

campaigns = st.Page(
    "pages/marketing/campaigns.py",
    title="Campaign Performance",
    icon="📣",
    url_path="marketing-campaigns",
)
attribution = st.Page(
    "pages/marketing/attribution.py",
    title="Marketing Attribution",
    icon="🎯",
    url_path="marketing-attribution",
)

reviews = st.Page(
    "pages/customer_experience/reviews.py",
    title="Reviews",
    icon="⭐",
    url_path="customer-experience-reviews",
)
support = st.Page(
    "pages/customer_experience/support.py",
    title="Customer Support",
    icon="🎧",
    url_path="customer-experience-support",
)

data_quality = st.Page(
    "pages/data_platform/data_quality.py",
    title="Data Quality",
    icon="🔍",
    url_path="data-platform-quality",
)
pipeline_health = st.Page(
    "pages/data_platform/pipeline_health.py",
    title="Pipeline Health",
    icon="⚙️",
    url_path="data-platform-pipeline",
)
model_performance = st.Page(
    "pages/data_platform/model_performance.py",
    title="Model Performance",
    icon="🏗️",
    url_path="data-platform-model-performance",
)

pg = st.navigation(
    {
        "🏠 Executive": [executive_command_center, executive_overview],
        "🛒 Commerce": [sales_overview, sales_funnel, orders, promotions],
        "👥 Customers": [customer_360, acquisition, retention],
        "🏷️ Products": [product_performance, catalogue_health],
        "📦 Operations": [inventory, fulfillment, shipping],
        "💳 Finance": [payments, revenue_profitability, returns_refunds, reconciliation],
        "📣 Marketing": [campaigns, attribution],
        "❤️ Customer Experience": [reviews, support],
        "⚙️ Data Platform": [data_quality, pipeline_health, model_performance],
    },
    position="top",
)

pg.run()
