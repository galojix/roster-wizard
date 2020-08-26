"""Views."""

from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

# from django.core.exceptions import PermissionDenied
from .models import CustomUser


class CustomUserListView(LoginRequiredMixin, ListView):
    """UserListView."""

    model = CustomUser
    template_name = "customuser_list.html"
    login_url = "login"

    def get_queryset(self):
        """Get query set."""
        return CustomUser.objects.order_by("last_name", "first_name")


class CustomUserDetailView(LoginRequiredMixin, DetailView):
    """UserDetailView."""

    model = CustomUser
    template_name = "customuser_detail.html"
    login_url = "login"


class CustomUserUpdateView(LoginRequiredMixin, UpdateView):
    """UserUpdateView."""

    model = CustomUser
    template_name = "customuser_update.html"
    fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "shifts_per_roster",
        "max_shifts",
        "available",
        "roles",
    )
    login_url = "login"


class CustomUserDeleteView(LoginRequiredMixin, DeleteView):
    """UserDeleteView."""

    model = CustomUser
    template_name = "customuser_delete.html"
    success_url = reverse_lazy("user_list")
    login_url = "login"


class CustomUserCreateView(LoginRequiredMixin, CreateView):
    """UserCreateView."""

    model = CustomUser
    template_name = "customuser_create.html"
    fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "shifts_per_roster",
        "max_shifts",
        "available",
        "roles",
    )
    login_url = "login"
