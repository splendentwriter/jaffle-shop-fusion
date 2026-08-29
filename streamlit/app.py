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
# row is [empty spacer, nav pills, status/Deploy/menu actions].
#
# Two earlier approaches both failed:
#  1. The classic flex trick (grow the spacer and the actions block by
#     equal amounts via flex-grow) only centers when both sides have equal
#     *minimum* content width. The actions block (Stop/Deploy/menu) has
#     real buttons with real min-width; the spacer is an empty div with
#     none, so flex-grow left it with only whatever space was left over -
#     visibly off-center.
#  2. Absolutely positioning the pills at the container's true horizontal
#     midpoint (left: 50%; transform: translateX(-50%)) fixed that, but
#     needed a max-width cap to keep the pills from reaching under the
#     actions block. Capping it via a *centered* max-width removes the
#     same amount from both sides - way more than the empty left side
#     ever needed - and on a ~500-650px window that cut deep enough to
#     leave no room for even one pill, collapsing the entire nav into a
#     single "N more" trigger. Reserving space asymmetrically (right-only)
#     instead doesn't fix it either: centering *within* a box that's
#     narrower on one side than the other just recreates the original
#     off-center bug at a fixed offset (half the reservation), at every
#     width, not only narrow ones.
#
# The actual fix: make both gutters *equal by construction* instead of
# trying to center around an inherently asymmetric layout. The actions
# block already gets a fixed width (below) so its footprint doesn't shift
# between idle and running (Stop button) states; giving the spacer that
# exact same fixed width makes the two flex-grow: 0 gutters truly
# identical, so the middle flex-grow: 1 slot they leave for the pills is
# symmetric around the real center - true centering, by geometry, with no
# fighting the nav widget's own native responsive-collapse sizing (which
# is what actually caused the ~500-650px collapse above: forcing it into
# an artificially tiny box via absolute positioning + max-width, rather
# than just giving it a real, correctly-sized flex slot to size itself
# within). Selectors are built from stable data-testid attributes plus
# structural pseudo-classes (:has, :empty, :last-child), not Streamlit's
# emotion-hash classnames, which change across builds.
st.markdown(
    """
    <style>
    [data-testid="stToolbar"] > div:has([data-testid="stTopNavSection"]) {
        display: flex;
        align-items: center;
        width: 100%;
    }
    [data-testid="stToolbar"] > div:has([data-testid="stTopNavSection"]) > div:empty:first-child,
    [data-testid="stToolbar"] > div:has([data-testid="stTopNavSection"]) > *:last-child {
        /* Fixed (not flex-grow) and identical on both sides, so the
           pills' flex-grow: 1 slot between them is exactly centered.
           210px comfortably covers the actions block's content
           (Stop+Deploy+menu, ~180px) with a little breathing room; the
           empty spacer just mirrors it with nothing to show. */
        flex: 0 0 210px;
    }
    [data-testid="stToolbar"] > div:has([data-testid="stTopNavSection"]) > *:last-child {
        display: flex;
        justify-content: flex-end;
    }
    [data-testid="stToolbar"] .rc-overflow {
        flex: 1 1 auto;
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
