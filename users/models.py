"""User models."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class CustomUser(AbstractUser):
    """Custom user model."""

    shifts_per_roster = models.IntegerField(null=False, blank=False)
    
    def __str__(self):
        """How a user object is displayed."""
        return self.last_name + ',' + self.first_name

    def get_absolute_url(self):
        """URL."""
        return reverse("user_detail", args=[str(self.id)])
