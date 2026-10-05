"""Prototype visual severity only: no physical depth, size, or hidden blockage."""
def visual_severity(relative_area: float) -> str:
    if relative_area < 0.03:
        return 'low'
    if relative_area < 0.12:
        return 'medium'
    return 'high'


def water_severity(coverage: float) -> str:
    if coverage <= 15:
        return 'low'
    if coverage <= 35:
        return 'medium'
    if coverage < 60:
        return 'high'
    return 'critical'
