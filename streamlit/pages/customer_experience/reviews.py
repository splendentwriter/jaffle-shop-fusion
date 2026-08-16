"""Reviews — rating distribution, response rate, and negative reviews needing attention."""

import plotly.express as px
import streamlit as st

from components.kpi_cards import kpi_row
from components.section_header import section_header
from queries.customer_experience import get_reviews
from utils.formatting import fmt_num, fmt_pct

section_header("Customer Experience", "Reviews", "⭐")

reviews = get_reviews()

kpi_row(
    [
        {"label": "Reviews", "value": fmt_num(len(reviews))},
        {"label": "Avg Rating", "value": f"{reviews['rating'].mean():.2f}"},
        {"label": "Response Rate", "value": fmt_pct(reviews["has_response"].mean())},
        {"label": "Negative Reviews", "value": fmt_num(reviews["is_negative"].sum())},
    ]
)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Rating distribution")
    rating_counts = reviews["rating"].value_counts().sort_index().reset_index()
    rating_counts.columns = ["Rating", "Count"]
    fig = px.bar(rating_counts, x="Rating", y="Count")
    st.plotly_chart(fig, width="stretch")

with col2:
    st.subheader("Status breakdown")
    status_counts = reviews["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    fig = px.pie(status_counts, names="Status", values="Count", hole=0.4)
    st.plotly_chart(fig, width="stretch")

st.subheader("Negative reviews without a response")
needs_attention = reviews[reviews["is_negative"] & ~reviews["has_response"]]
st.caption(f"{fmt_num(len(needs_attention))} negative reviews have no response yet.")
if not needs_attention.empty:
    st.dataframe(
        needs_attention[["product_name", "title", "rating", "helpful_votes", "not_helpful_votes", "created_at"]].rename(
            columns={
                "product_name": "Product",
                "title": "Title",
                "rating": "Rating",
                "helpful_votes": "Helpful",
                "not_helpful_votes": "Not Helpful",
                "created_at": "Created",
            }
        ),
        width="stretch",
        hide_index=True,
    )
