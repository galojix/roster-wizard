"""Serializers."""

from datetime import datetime
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


class DateTimeSerializer(serializers.Serializer):
    """DateTime Serializer."""

    date = serializers.DateTimeField()

    def create(self, validated_data):
        """Create date."""
        return datetime(**validated_data)

    def update(self, instance, validated_data):
        """Update date."""
        instance.date = validated_data.get("date", instance.date)
        return instance
