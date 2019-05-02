from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import CustomUser
from rosters.models import Role


class UserListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = "user_list.html"
    login_url = "login"

    def get_queryset(self):
        return CustomUser.objects.order_by("username")


class UserDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "user_detail.html"
    login_url = "login"


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    template_name = "user_edit.html"
    fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "shifts_per_roster",
        "roles",
    )
    login_url = "login"


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = "user_delete.html"
    success_url = reverse_lazy("user_list")
    login_url = "login"


class UserCreateView(LoginRequiredMixin, CreateView):
    model = CustomUser
    template_name = "user_new.html"
    fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "shifts_per_roster",
        "roles",
    )
    login_url = "login"
