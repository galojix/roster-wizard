"""User models."""
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.urls import reverse


class CustomUserManager(UserManager):
    """CustomUser Manager."""

    def get_queryset(self):
        """Select additional related object data."""
        query_set = super().get_queryset()
        return query_set.prefetch_related("roles")


class CustomUser(AbstractUser):
    """Custom user model."""

    class Meta:
        """Meta."""

        ordering = ("last_name", "first_name")

    objects = CustomUserManager()
    available = models.BooleanField(null=False, blank=False, default=True)
    shifts_per_roster = models.IntegerField(null=False, blank=False, default=0)
    max_shifts = models.BooleanField(null=False, blank=False, default=True)
    roles = models.ManyToManyField("rosters.Role")

    def __str__(self):
        """How a user object is displayed."""
        return self.last_name + "," + self.first_name

    def get_absolute_url(self):
        """URL."""
        return reverse("customuser_detail", args=[str(self.id)])
