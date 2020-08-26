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
    template_name = "custom_user_list.html"
    context_object_name = "custom_user_list"
    login_url = "login"

    def get_queryset(self):
        """Get query set."""
        return CustomUser.objects.order_by("last_name", "first_name")


class CustomUserDetailView(LoginRequiredMixin, DetailView):
    """UserDetailView."""

    model = CustomUser
    template_name = "custom_user_detail.html"
    context_object_name = "custom_user"
    login_url = "login"


class CustomUserUpdateView(LoginRequiredMixin, UpdateView):
    """UserUpdateView."""

    model = CustomUser
    template_name = "custom_user_update.html"
    context_object_name = "custom_user"
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
    template_name = "custom_user_delete.html"
    success_url = reverse_lazy("user_list")
    context_object_name = "custom_user"
    login_url = "login"


class CustomUserCreateView(LoginRequiredMixin, CreateView):
    """UserCreateView."""

    model = CustomUser
    template_name = "custom_user_create.html"
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
