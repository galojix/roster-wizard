"""Custom Template Tags."""

from django import template
register = template.Library()


@register.filter
def index(List, i):
    """Get list element via index."""
    return List[int(i)]
