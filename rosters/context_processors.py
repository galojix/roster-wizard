"""Context Processors."""
from django.conf import settings


def get_roster_name(request):
    """Get roster name from settings."""
    return {"roster_name": settings.ROSTER_NAME}
