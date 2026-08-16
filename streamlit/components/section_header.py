"""Consistent per-page header: business-section breadcrumb + page title."""

import streamlit as st


def section_header(section: str, title: str, icon: str = ""):
    st.caption(section.upper())
    st.title(f"{icon} {title}" if icon else title)
