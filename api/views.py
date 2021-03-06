"""Views."""

from rest_framework import viewsets, status
from rest_framework.response import Response


from rosters.models import Leave, TimeSlot
from .serializers import (
    LeaveSerializer,
    TimeSlotSerializer,
    DateTimeSerializer,
)

from rosters.tasks import generate_roster

# from celery.result import AsyncResult


class LeaveViewSet(viewsets.ModelViewSet):
    """LeaveViewSet."""

    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer


class TimeSlotViewSet(viewsets.ModelViewSet):
    """TimeSlotViewSet."""

    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer


class GenerateRosterViewSet(viewsets.ViewSet):
    """GenerateRosterView."""

    def list(self, request):
        """Get page."""
        data = {"date": "required"}
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request):
        """Generate roster with given start date."""
        serializer = DateTimeSerializer(data=request.data)
        if serializer.is_valid():
            date = serializer.validated_data["date"]
            result = generate_roster.delay(start_date=date)
            data = {"task": result.task_id}
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Not used."""
        pass

    def update(self, request, pk=None):
        """Not used."""
        pass

    def partial_update(self, request, pk=None):
        """Not used."""
        pass

    def destroy(self, request, pk=None):
        """Not used."""
        pass
