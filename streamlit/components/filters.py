"""Reusable filter widgets. These render controls and return the selected
value(s) — callers decide how (or whether) to apply them to a dataframe.
Kept generic on purpose: most existing pages already push their filtering
into dbt marts, so this is for pages that filter an already-fetched
dataframe in pandas, not a mechanism for adding new WHERE clauses to
existing queries."""

import streamlit as st


def category_filter(label: str, options, *, all_label: str = "All", key: str | None = None):
    """Renders a selectbox with a leading 'All' option. Returns None when
    'All' is selected, otherwise the chosen value."""
    choice = st.selectbox(label, [all_label] + list(options), key=key)
    return None if choice == all_label else choice


def apply_category_filter(df, column: str, selected):
    return df if selected is None else df[df[column] == selected]
