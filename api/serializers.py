"""Serializers."""

# from django.contrib.auth import get_user_model # new
from rest_framework import serializers
from rosters.models import TimeSlot, Leave


class LeaveSerializer(serializers.ModelSerializer):
    """Leave Serilizer."""

    class Meta:
        """Meta."""

        model = Leave
        fields = (
            "id",
            "date",
            "description",
            "staff_member",
        )


class TimeSlotSerializer(serializers.ModelSerializer):
    """TimeSlot Serializer."""

    class Meta:
        """Meta."""

        model = TimeSlot
        fields = (
            "id",
            "date",
            "staff",
            "shift",
        )
