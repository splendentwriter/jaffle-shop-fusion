"""Jaffle Shop — Analytics Command Center application shell.

Defines the business-operation navigation (Executive, Commerce, Customers,
Products, Operations, Finance, Marketing, Customer Experience, HR &
Payroll, Data Platform) and hands off to the selected page. No business
logic lives
here — see CONVENTIONS.md in the repo root: dbt owns business logic,
Streamlit only presents it.
"""

import streamlit as st

from utils.config import APP_ICON, APP_TITLE

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

# Center the top-position nav pills within the header toolbar. The toolbar
# row is [empty spacer, nav pills, status/Deploy/menu actions]. An earlier
# version tried the classic flex trick (grow the spacer and the actions
# block by equal amounts), but that only centers the pills when both sides
# have equal *minimum* content width - the actions block (Stop/Deploy/menu)
# has real buttons with a real min-width, while the spacer is an empty div
# with none, so flex-grow left the spacer with only whatever space was left
# over rather than a true 50/50 split, and the pills sat visibly left of
# center. Anchoring the pills with absolute positioning at the container's
# actual horizontal midpoint sidesteps that entirely: it's centered on the
# full toolbar width regardless of what either side's content measures out
# to, and recalculates on every resize since it's pure CSS, not a one-time
# JS measurement. Selectors are built from stable data-testid attributes
# plus structural pseudo-classes (:has, :empty, :last-child), not
# Streamlit's emotion-hash classnames, which change across builds.
st.markdown(
    """
    <style>
    [data-testid="stToolbar"] > div:has([data-testid="stTopNavSection"]) {
        position: relative;
        display: block;
        width: 100%;
        min-height: 2rem;
    }
    [data-testid="stToolbar"] > div:has([data-testid="stTopNavSection"]) > div:empty:first-child {
        display: none;
    }
    [data-testid="stToolbar"] > div:has([data-testid="stTopNavSection"]) > *:last-child {
        position: absolute;
        top: 50%;
        right: 0;
        transform: translateY(-50%);
        /* This block gains a "Stop" button while a script run is in
           flight, widening it from ~90px to ~165px. Reserving that width
           up front keeps its footprint constant regardless of run state,
           so the nav-pill row's own responsive collapse (which measures
           available space once, not continuously) doesn't get caught out
           mid-run and butt up against a newly-appeared Stop button. */
        min-width: 180px;
        display: flex;
        justify-content: flex-end;
    }
    /* The nav pill row (rc-overflow, an ant-design-family component) ships
       its own width: 100% rule that greedily fills all space handed to it;
       pin it to its actual content width (!important needed to beat that
       rule's classname-based specificity) so it can be centered on its own
       footprint rather than stretching edge-to-edge. max-width leaves a
       little headroom past the reserved actions block above, as a second
       line of defense against overlap. */
    [data-testid="stToolbar"] .rc-overflow {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: fit-content !important;
        max-width: calc(100% - 400px);
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

employees = st.Page("pages/hr/employees.py", title="Employees", icon="👤", url_path="hr-employees")
payroll = st.Page("pages/hr/payroll.py", title="Payroll", icon="🧑‍💼", url_path="hr-payroll")

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
        "🧑‍💼 HR & Payroll": [employees, payroll],
        "⚙️ Data Platform": [data_quality, pipeline_health, model_performance],
    },
    position="top",
)

pg.run()
