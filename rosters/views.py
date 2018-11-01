from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import Leave


class LeaveListView(LoginRequiredMixin, ListView):
    model = Leave
    template_name = 'leave_list.html'
    login_url = 'login'


class LeaveDetailView(LoginRequiredMixin, DetailView):
    model = Leave
    template_name = 'leave_detail.html'
    login_url = 'login'


class LeaveUpdateView(LoginRequiredMixin, UpdateView):
    model = Leave
    fields = ('title', 'body',)
    template_name = 'leave_edit.html'
    login_url = 'login'


class LeaveDeleteView(LoginRequiredMixin, DeleteView):
    model = Leave
    template_name = 'leave_delete.html'
    success_url = reverse_lazy('leave_list')
    login_url = 'login'


class LeaveCreateView(LoginRequiredMixin, CreateView):
    model = Leave
    template_name = 'leave_new.html'
    fields = ('title', 'body')
    login_url = 'login'
