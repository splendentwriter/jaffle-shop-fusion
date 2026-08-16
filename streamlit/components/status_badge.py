"""Consistent health-status badge (🟢🟡🔴) for KPI/health indicators."""


def status_badge(is_good: bool, is_watch: bool) -> str:
    if is_good:
        return "🟢 Strong"
    if is_watch:
        return "🟡 Watch"
    return "🔴 Attention"
