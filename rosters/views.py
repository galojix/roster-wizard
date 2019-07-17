import datetime
import csv
from django.views.generic import ListView, DetailView
from django.views.generic.edit import (
    UpdateView,
    DeleteView,
    CreateView,
    FormView,
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from rosters.forms import GenerateRosterForm, SelectRosterForm

from .models import (
    Leave,
    Role,
    Shift,
    ShiftRule,
    ShiftRuleRole,
    StaffRule,
    StaffRuleShift,
    TimeSlot,
    Preference,
)
from .forms import (
    LeaveCreateForm,
    LeaveUpdateForm,
    TimeSlotUpdateForm,
    TimeSlotCreateForm,
    StaffRuleUpdateForm,
)
from .logic import SolutionNotFeasible, generate_roster, get_roster_by_staff


class LeaveListView(LoginRequiredMixin, ListView):
    model = Leave
    template_name = "leave_list.html"
    login_url = "login"


class LeaveDetailView(LoginRequiredMixin, DetailView):
    model = Leave
    template_name = "leave_detail.html"
    login_url = "login"


class LeaveUpdateView(LoginRequiredMixin, UpdateView):
    model = Leave
    form_class = LeaveUpdateForm
    template_name = "leave_edit.html"
    login_url = "login"


class LeaveDeleteView(LoginRequiredMixin, DeleteView):
    model = Leave
    template_name = "leave_delete.html"
    success_url = reverse_lazy("leave_list")
    login_url = "login"


class LeaveCreateView(LoginRequiredMixin, CreateView):
    model = Leave
    template_name = "leave_new.html"
    form_class = LeaveCreateForm
    # fields = ('date', 'staff_member')
    login_url = "login"


class RoleListView(LoginRequiredMixin, ListView):
    model = Role
    template_name = "role_list.html"
    login_url = "login"

    def get_queryset(self):
        return Role.objects.order_by("role_name")


class RoleDetailView(LoginRequiredMixin, DetailView):
    model = Role
    template_name = "role_detail.html"
    login_url = "login"


class RoleUpdateView(LoginRequiredMixin, UpdateView):
    model = Role
    fields = ("role_name",)
    template_name = "role_edit.html"
    login_url = "login"


class RoleDeleteView(LoginRequiredMixin, DeleteView):
    model = Role
    template_name = "role_delete.html"
    success_url = reverse_lazy("role_list")
    login_url = "login"


class RoleCreateView(LoginRequiredMixin, CreateView):
    model = Role
    template_name = "role_new.html"
    fields = ("role_name",)
    login_url = "login"


class ShiftListView(LoginRequiredMixin, ListView):
    model = Shift
    template_name = "shift_list.html"
    login_url = "login"


class ShiftDetailView(LoginRequiredMixin, DetailView):
    model = Shift
    template_name = "shift_detail.html"
    login_url = "login"


class ShiftUpdateView(LoginRequiredMixin, UpdateView):
    model = Shift
    fields = (
        "shift_type",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    )
    template_name = "shift_edit.html"
    login_url = "login"


class ShiftDeleteView(LoginRequiredMixin, DeleteView):
    model = Shift
    template_name = "shift_delete.html"
    success_url = reverse_lazy("shift_list")
    login_url = "login"


class ShiftCreateView(LoginRequiredMixin, CreateView):
    model = Shift
    template_name = "shift_new.html"
    fields = (
        "shift_type",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    )
    login_url = "login"


class ShiftRuleListView(LoginRequiredMixin, ListView):
    model = ShiftRule
    template_name = "shift_rule_list.html"
    login_url = "login"

    def get_queryset(self):
        return ShiftRule.objects.order_by("shift", "shift_rule_name")


class ShiftRuleDetailView(LoginRequiredMixin, DetailView):
    model = ShiftRule
    template_name = "shift_rule_detail.html"
    login_url = "login"


class ShiftRuleUpdateView(LoginRequiredMixin, UpdateView):
    model = ShiftRule
    fields = ("shift_rule_name", "shift")
    template_name = "shift_rule_edit.html"
    login_url = "login"


class ShiftRuleDeleteView(LoginRequiredMixin, DeleteView):
    model = ShiftRule
    template_name = "shift_rule_delete.html"
    success_url = reverse_lazy("shift_rule_list")
    login_url = "login"


class ShiftRuleCreateView(LoginRequiredMixin, CreateView):
    model = ShiftRule
    template_name = "shift_rule_new.html"
    fields = ("shift_rule_name", "shift")
    login_url = "login"


class ShiftRuleRoleListView(LoginRequiredMixin, ListView):
    model = ShiftRuleRole
    template_name = "shift_rule_role_list.html"
    login_url = "login"

    def get_queryset(self):
        return ShiftRuleRole.objects.order_by("shift_rule", "role")


class ShiftRuleRoleDetailView(LoginRequiredMixin, DetailView):
    model = ShiftRuleRole
    template_name = "shift_rule_role_detail.html"
    login_url = "login"


class ShiftRuleRoleUpdateView(LoginRequiredMixin, UpdateView):
    model = ShiftRuleRole
    fields = ("shift_rule", "role", "count")
    template_name = "shift_rule_role_edit.html"
    login_url = "login"


class ShiftRuleRoleDeleteView(LoginRequiredMixin, DeleteView):
    model = ShiftRuleRole
    template_name = "shift_rule_role_delete.html"
    success_url = reverse_lazy("shift_rule_list")
    login_url = "login"


class ShiftRuleRoleCreateView(LoginRequiredMixin, CreateView):
    model = ShiftRuleRole
    template_name = "shift_rule_role_new.html"
    fields = ("role", "count")
    login_url = "login"

    def form_valid(self, form):
        shift_rule = get_object_or_404(ShiftRule, id=self.kwargs["shiftrule"])
        form.instance.shift_rule = shift_rule
        return super().form_valid(form)


class StaffRuleListView(LoginRequiredMixin, ListView):
    model = StaffRule
    template_name = "staff_rule_list.html"
    login_url = "login"

    def get_queryset(self):
        return StaffRule.objects.order_by("staff_rule_name")


class StaffRuleDetailView(LoginRequiredMixin, DetailView):
    model = StaffRule
    template_name = "staff_rule_detail.html"
    login_url = "login"


class StaffRuleUpdateView(LoginRequiredMixin, UpdateView):
    model = StaffRule
    # fields = ("staff_rule_name", "staff")
    form_class = StaffRuleUpdateForm
    template_name = "staff_rule_edit.html"
    login_url = "login"


class StaffRuleDeleteView(LoginRequiredMixin, DeleteView):
    model = StaffRule
    template_name = "staff_rule_delete.html"
    success_url = reverse_lazy("staff_rule_list")
    login_url = "login"


class StaffRuleCreateView(LoginRequiredMixin, CreateView):
    model = StaffRule
    template_name = "staff_rule_new.html"
    fields = ("staff_rule_name", "staff")
    login_url = "login"


class StaffRuleShiftListView(LoginRequiredMixin, ListView):
    model = StaffRuleShift
    template_name = "staff_rule_shift_list.html"
    login_url = "login"


class StaffRuleShiftDetailView(LoginRequiredMixin, DetailView):
    model = StaffRuleShift
    template_name = "staff_rule_shift_detail.html"
    success_url = reverse_lazy("staff_rule_list")
    login_url = "login"


class StaffRuleShiftUpdateView(LoginRequiredMixin, UpdateView):
    model = StaffRuleShift
    fields = ("shift", "position")
    template_name = "staff_rule_shift_edit.html"
    success_url = reverse_lazy("staff_rule_list")
    login_url = "login"


class StaffRuleShiftDeleteView(LoginRequiredMixin, DeleteView):
    model = StaffRuleShift
    template_name = "staff_rule_shift_delete.html"
    success_url = reverse_lazy("staff_rule_list")
    login_url = "login"


class StaffRuleShiftCreateView(LoginRequiredMixin, CreateView):
    model = StaffRuleShift
    template_name = "staff_rule_shift_new.html"
    fields = ("shift", "position")
    login_url = "login"

    def form_valid(self, form):
        staff_rule = get_object_or_404(StaffRule, id=self.kwargs["staffrule"])
        form.instance.staff_rule = staff_rule
        return super().form_valid(form)


class TimeSlotListView(LoginRequiredMixin, ListView):
    model = TimeSlot
    template_name = "timeslot_list.html"
    login_url = "login"

    def get_queryset(self):
        print(self.request.session)
        if (
            "start_date" in self.request.session
            and "num_days" in self.request.session
        ):
            start_date = datetime.datetime.strptime(
                self.request.session["start_date"], "%d-%b-%Y"
            )
            num_days = datetime.timedelta(
                days=self.request.session["num_days"]
            )
            end_date = start_date + num_days
            date_range = [start_date, end_date]
            return TimeSlot.objects.filter(date__range=date_range).order_by(
                "date", "shift__shift_type"
            )
        else:
            return TimeSlot.objects.order_by("date", "shift__shift_type")


class RosterListView(LoginRequiredMixin, ListView):
    model = TimeSlot
    template_name = "roster_list.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if (
            "start_date" in self.request.session
            and "num_days" in self.request.session
        ):
            start_date = datetime.datetime.strptime(
                self.request.session["start_date"], "%d-%b-%Y"
            )
            num_days = self.request.session["num_days"]
        else:
            start_date = datetime.datetime.now()
            num_days = 14
        dates, roster = get_roster_by_staff(start_date, num_days)
        context["dates"] = dates
        context["roster"] = roster
        return context


class TimeSlotDetailView(LoginRequiredMixin, DetailView):
    model = TimeSlot
    template_name = "timeslot_detail.html"
    login_url = "login"


class TimeSlotUpdateView(LoginRequiredMixin, UpdateView):
    model = TimeSlot
    form_class = TimeSlotUpdateForm
    template_name = "timeslot_edit.html"
    login_url = "login"


class TimeSlotDeleteView(LoginRequiredMixin, DeleteView):
    model = TimeSlot
    template_name = "timeslot_delete.html"
    success_url = reverse_lazy("timeslot_list")
    login_url = "login"


class TimeSlotCreateView(LoginRequiredMixin, CreateView):
    model = TimeSlot
    form_class = TimeSlotCreateForm
    template_name = "timeslot_new.html"
    login_url = "login"


class SelectRosterView(LoginRequiredMixin, FormView):
    template_name = "select_roster.html"
    form_class = SelectRosterForm
    success_url = reverse_lazy("timeslot_list")

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        start_date = form.cleaned_data["start_date"]
        num_days = form.cleaned_data["num_days"]
        self.request.session["start_date"] = start_date.date().strftime(
            "%d-%b-%Y"
        )
        self.request.session["num_days"] = num_days
        return super().form_valid(form)


class GenerateRosterView(LoginRequiredMixin, FormView):
    template_name = "generate_roster.html"
    form_class = GenerateRosterForm
    success_url = reverse_lazy("roster_list")

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        start_date = form.cleaned_data["start_date"]
        num_days = form.cleaned_data["num_days"]
        try:
            generate_roster(start_date, num_days)
        except SolutionNotFeasible:
            messages.error(
                self.request,
                (
                    "Could not generate roster,"
                    " try changing rules or staff availability."
                ),
            )
        return super().form_valid(form)


class PreferenceListView(LoginRequiredMixin, ListView):
    model = Preference
    template_name = "preference_list.html"
    login_url = "login"


class PreferenceDetailView(LoginRequiredMixin, DetailView):
    model = Preference
    template_name = "preference_detail.html"
    login_url = "login"


class PreferenceUpdateView(LoginRequiredMixin, UpdateView):
    model = Preference
    # form_class = PreferenceUpdateForm
    fields = ("day", "shift", "priority")
    template_name = "preference_edit.html"
    login_url = "login"


class PreferenceDeleteView(LoginRequiredMixin, DeleteView):
    model = Preference
    template_name = "preference_delete.html"
    success_url = reverse_lazy("preference_list")
    login_url = "login"


class PreferenceCreateView(LoginRequiredMixin, CreateView):
    model = Preference
    template_name = "preference_new.html"
    # form_class = PreferenceCreateForm
    fields = ("staff_member", "day", "shift", "priority")
    login_url = "login"


@login_required
def download_csv(request):
    if "start_date" in request.session and "num_days" in request.session:
        start_date = datetime.datetime.strptime(
            request.session["start_date"], "%d-%b-%Y"
        )
        num_days = request.session["num_days"]
    else:
        start_date = datetime.datetime.now()
        num_days = 14

    dates, roster = get_roster_by_staff(start_date, num_days)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="roster.csv"'

    writer = csv.writer(response)
    dates = [date.strftime("%a %d-%b-%Y") for date in dates]
    row = ["Staff Member", "Roles"] + dates
    writer.writerow(row)
    for staff_member in roster:
        row = [staff_member]
        for key in roster[staff_member]:
            row.append(roster[staff_member][key])
        writer.writerow(row)
    return response
