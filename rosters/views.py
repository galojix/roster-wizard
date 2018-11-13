from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import (
    Leave,
    Role,
    Shift,
    ShiftRule,
    StaffRule,
    TimeSlot,
)
from .forms import (
    LeaveCreateForm,
    LeaveUpdateForm,
)


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
    form_class = LeaveUpdateForm
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
    form_class = LeaveCreateForm
    # fields = ('date', 'staff_member')
    login_url = 'login'


class RoleListView(LoginRequiredMixin, ListView):
    model = Role
    template_name = 'role_list.html'
    login_url = 'login'


class RoleDetailView(LoginRequiredMixin, DetailView):
    model = Role
    template_name = 'role_detail.html'
    login_url = 'login'


class RoleUpdateView(LoginRequiredMixin, UpdateView):
    model = Role
    fields = ('role_name', 'staff')
    template_name = 'role_edit.html'
    login_url = 'login'


class RoleDeleteView(LoginRequiredMixin, DeleteView):
    model = Role
    template_name = 'role_delete.html'
    success_url = reverse_lazy('role_list')
    login_url = 'login'


class RoleCreateView(LoginRequiredMixin, CreateView):
    model = Role
    template_name = 'role_new.html'
    fields = ('role_name', 'staff')
    login_url = 'login'


class ShiftListView(LoginRequiredMixin, ListView):
    model = Shift
    template_name = 'shift_list.html'
    login_url = 'login'


class ShiftDetailView(LoginRequiredMixin, DetailView):
    model = Shift
    template_name = 'shift_detail.html'
    login_url = 'login'


class ShiftUpdateView(LoginRequiredMixin, UpdateView):
    model = Shift
    fields = (
        'shift_type',
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday',
    )
    template_name = 'shift_edit.html'
    login_url = 'login'


class ShiftDeleteView(LoginRequiredMixin, DeleteView):
    model = Shift
    template_name = 'shift_delete.html'
    success_url = reverse_lazy('shift_list')
    login_url = 'login'


class ShiftCreateView(LoginRequiredMixin, CreateView):
    model = Shift
    template_name = 'shift_new.html'
    fields = (
        'shift_type',
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday',
    )
    login_url = 'login'


class ShiftRuleListView(LoginRequiredMixin, ListView):
    model = ShiftRule
    template_name = 'shift_rule_list.html'
    login_url = 'login'


class ShiftRuleDetailView(LoginRequiredMixin, DetailView):
    model = ShiftRule
    template_name = 'shift_rule_detail.html'
    login_url = 'login'


class ShiftRuleUpdateView(LoginRequiredMixin, UpdateView):
    model = ShiftRule
    fields = ('title', 'body',)
    template_name = 'shift_rule_edit.html'
    login_url = 'login'


class ShiftRuleDeleteView(LoginRequiredMixin, DeleteView):
    model = ShiftRule
    template_name = 'shift_rule_delete.html'
    success_url = reverse_lazy('shift_rule_list')
    login_url = 'login'


class ShiftRuleCreateView(LoginRequiredMixin, CreateView):
    model = ShiftRule
    template_name = 'shift_rule_new.html'
    fields = ('title', 'body')
    login_url = 'login'


class StaffRuleListView(LoginRequiredMixin, ListView):
    model = StaffRule
    template_name = 'staff_rule_list.html'
    login_url = 'login'


class StaffRuleDetailView(LoginRequiredMixin, DetailView):
    model = StaffRule
    template_name = 'staff_rule_detail.html'
    login_url = 'login'


class StaffRuleUpdateView(LoginRequiredMixin, UpdateView):
    model = StaffRule
    fields = ('title', 'body',)
    template_name = 'staff_rule_edit.html'
    login_url = 'login'


class StaffRuleDeleteView(LoginRequiredMixin, DeleteView):
    model = StaffRule
    template_name = 'staff_rule_delete.html'
    success_url = reverse_lazy('staff_rule_list')
    login_url = 'login'


class StaffRuleCreateView(LoginRequiredMixin, CreateView):
    model = StaffRule
    template_name = 'staff_rule_new.html'
    fields = ('title', 'body')
    login_url = 'login'


class TimeSlotListView(LoginRequiredMixin, ListView):
    model = TimeSlot
    template_name = 'timeslot_list.html'
    login_url = 'login'


class TimeSlotDetailView(LoginRequiredMixin, DetailView):
    model = TimeSlot
    template_name = 'timeslot_detail.html'
    login_url = 'login'


class TimeSlotUpdateView(LoginRequiredMixin, UpdateView):
    model = TimeSlot
    fields = ('title', 'body',)
    template_name = 'timeslot_edit.html'
    login_url = 'login'


class TimeSlotDeleteView(LoginRequiredMixin, DeleteView):
    model = TimeSlot
    template_name = 'timeslot_delete.html'
    success_url = reverse_lazy('timeslot_list')
    login_url = 'login'


class TimeSlotCreateView(LoginRequiredMixin, CreateView):
    model = TimeSlot
    template_name = 'timeslot_new.html'
    fields = ('title', 'body')
    login_url = 'login'
