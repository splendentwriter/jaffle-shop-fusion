"""Reusable KPI card row, built on st.metric."""

import streamlit as st

from utils.formatting import fmt_pct


def kpi_row(cards: list[dict]):
    """cards: list of {"label": str, "value": str, "delta": float|None (a
    fraction, e.g. 0.184 for +18.4%) or None to omit the delta}."""
    columns = st.columns(len(cards))
    for column, card in zip(columns, cards):
        delta = card.get("delta")
        column.metric(
            label=card["label"],
            value=card["value"],
            delta=fmt_pct(delta) if delta is not None else None,
        )
