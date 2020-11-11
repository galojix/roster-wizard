"""Context Processors."""
from django.conf import settings


def get_roster_name(request):
    """Get roster name from settings."""
    return {"roster_name": settings.ROSTER_NAME}


def get_shift_seq_valid(request):
    """Get shift sequence logic from settings."""
    return {"shift_seq_valid": settings.SHIFT_SEQ_VALID}
