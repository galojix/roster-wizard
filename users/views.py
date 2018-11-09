from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import CustomUser


class UserListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'user_list.html'
    login_url = 'login'


class UserDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'user_detail.html'
    login_url = 'login'


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    template_name = 'user_edit.html'
    fields = ('username', 'first_name', 'last_name', 'email', 'ward_name')
    login_url = 'login'


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'user_delete.html'
    success_url = reverse_lazy('user_list')
    login_url = 'login'


class UserCreateView(LoginRequiredMixin, CreateView):
    model = CustomUser
    template_name = 'user_new.html'
    fields = ('username', 'first_name', 'last_name', 'email', 'ward_name')
    login_url = 'login'
