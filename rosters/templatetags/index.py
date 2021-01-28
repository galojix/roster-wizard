"""Custom Template Tags."""

from django import template

register = template.Library()


@register.filter
def index(List, i):
    """Get list element via index."""
    return List[int(i)]


# @register.filter
# def index_div_by_3(List, i):
#     """Get list element via index."""
#     i = i / 3
#     return List[int(i)]


@register.filter
def index_div_by_2(List, i):
    """Get list element via index."""
    i = i / 2
    return List[int(i)]
