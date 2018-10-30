"""User forms."""
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form."""

    class Meta(UserCreationForm.Meta):
        """Meta data."""

        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('ward_name',)


class CustomUserChangeForm(UserChangeForm):
    """Custom user change form."""

    class Meta:
        """Meta data."""

        model = CustomUser
        fields = UserChangeForm.Meta.fields
