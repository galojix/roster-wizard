"""Views."""

# from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rosters.models import Leave, TimeSlot
from .serializers import LeaveSerializer, TimeSlotSerializer


class LeaveViewSet(viewsets.ModelViewSet):
    """LeaveViewSet."""

    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer


class TimeSlotViewSet(viewsets.ModelViewSet):
    """TimeSlotViewSet."""

    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
