"""User models."""
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.urls import reverse


class CustomUserManager(BaseUserManager):
    """CustomUser Manager."""

    def get_queryset(self):
        """Select additional related object data."""
        query_set = super().get_queryset()
        return query_set.prefetch_related("roles")

    def create_user(self, username, password, **extra_fields):
        """Create and save a User with the given username and password."""
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        """Create and save a SuperUser with the given username and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractUser):
    """Custom user model."""

    class Meta:
        """Meta."""

        ordering = ("last_name", "first_name")

    objects = CustomUserManager()
    available = models.BooleanField(null=False, blank=False, default=True)
    shifts_per_roster = models.IntegerField(null=False, blank=False, default=0)
    max_shifts = models.BooleanField(null=False, blank=False, default=True)
    roles = models.ManyToManyField("rosters.Role", blank=True)
    enforce_shifts_per_roster = models.BooleanField(
        null=False, blank=False, default=True
    )
    enforce_one_shift_per_day = models.BooleanField(
        null=False, blank=False, default=True
    )

    def __str__(self):
        """How a user object is displayed."""
        return self.last_name + "," + self.first_name

    def get_absolute_url(self):
        """URL."""
        return reverse("customuser_detail", args=[str(self.id)])
