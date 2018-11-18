"""User models."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class CustomUser(AbstractUser):
    """Custom user model."""

    ward_name = models.CharField(max_length=40, blank=True)

    def __str__(self):
        """How a user object is displayed."""
        return self.username

    def get_absolute_url(self):
        """URL."""
        return reverse("user_detail", args=[str(self.id)])
