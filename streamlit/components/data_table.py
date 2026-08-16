"""Thin wrapper around st.dataframe with the project's default styling."""

import streamlit as st


def data_table(df, rename: dict | None = None, **kwargs):
    if rename:
        df = df.rename(columns=rename)
    kwargs.setdefault("width", "stretch")
    kwargs.setdefault("hide_index", True)
    st.dataframe(df, **kwargs)
