"""Small styled callout for an opportunity, risk, or trend on the Command Center."""

import streamlit as st

_RENDERERS = {"info": st.info, "success": st.success, "warning": st.warning, "error": st.error}


def insight_card(text: str, kind: str = "info"):
    """kind: one of 'info', 'success', 'warning', 'error'."""
    _RENDERERS.get(kind, st.info)(text)
