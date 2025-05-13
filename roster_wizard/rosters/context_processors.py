"""Context Processors."""
# from django.conf import settings
from .models import RosterSettings


def get_roster_name(request):
    """Get roster name from settings."""
    if RosterSettings.objects.exists():
        return {"roster_name": RosterSettings.objects.first().roster_name}
    else:
        return {"roster_name": "No Location Set"}
