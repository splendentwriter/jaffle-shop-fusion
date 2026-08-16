"""Thin wrappers around Plotly Express with the project's default chart layout."""

import plotly.express as px


def line_chart(df, x, y, height=380, **kwargs):
    fig = px.line(df, x=x, y=y, markers=True, **kwargs)
    fig.update_layout(height=height)
    return fig


def bar_chart(df, x, y, height=380, **kwargs):
    fig = px.bar(df, x=x, y=y, **kwargs)
    fig.update_layout(height=height)
    return fig
