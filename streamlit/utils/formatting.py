"""Display-only formatting helpers. No metric derivation — that's dbt's job."""


def fmt_usd(value, decimals=0) -> str:
    if value is None:
        return "—"
    return f"${value:,.{decimals}f}"


def fmt_pct(value, decimals=1) -> str:
    """value is a fraction (0.1672), not already multiplied by 100."""
    if value is None:
        return "—"
    return f"{value * 100:,.{decimals}f}%"


def fmt_num(value) -> str:
    if value is None:
        return "—"
    return f"{value:,.0f}"


def fmt_month(value) -> str:
    if value is None:
        return "—"
    return value.strftime("%B %Y")
