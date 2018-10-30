"""User models."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model."""

    ward_name = models.CharField(max_length=40, blank=True)
