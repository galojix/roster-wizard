"""Views."""

import datetime
import csv

from collections import OrderedDict

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
from django.contrib.auth import get_user_model

from .models import (
    Leave,
    Role,
    Shift,
    ShiftRule,
    ShiftRuleRole,
    StaffRule,
    StaffRuleShift,
    TimeSlot,
    StaffRequest,
    DayGroup,
    Day,
    DayGroupDay,
)
from .forms import (
    LeaveCreateForm,
    LeaveUpdateForm,
    TimeSlotUpdateForm,
    TimeSlotCreateForm,
    StaffRuleUpdateForm,
    StaffRuleCreateForm,
    DaySetCreateForm,
    GenerateRosterForm,
    SelectRosterForm,
    StaffRequestUpdateForm,
)
from .logic import (
    SolutionNotFeasible,
    TooManyStaff,
    RosterGenerator,
    get_roster_by_staff,
)


class LeaveListView(LoginRequiredMixin, ListView):
    """Leave List View."""

    model = Leave
    template_name = "leave_list.html"
    login_url = "login"

    def get_queryset(self):
        """Get leave in date range."""
        if "start_date" in self.request.session:
            start_date = datetime.datetime.strptime(
                self.request.session["start_date"], "%d-%b-%Y"
            )
        else:
            start_date = datetime.datetime.now()
        num_days = datetime.timedelta(days=Day.objects.count() - 1)
        end_date = start_date + num_days
        date_range = [start_date, end_date]
        return Leave.objects.filter(date__range=date_range)


class LeaveDetailView(LoginRequiredMixin, DetailView):
    """Leave Detail View."""

    model = Leave
    template_name = "leave_detail.html"
    login_url = "login"


class LeaveUpdateView(LoginRequiredMixin, UpdateView):
    """Leave Update View."""

    model = Leave
    form_class = LeaveUpdateForm
    template_name = "leave_update.html"
    login_url = "login"


class LeaveDeleteView(LoginRequiredMixin, DeleteView):
    """Leave Delete View."""

    model = Leave
    template_name = "leave_delete.html"
    success_url = reverse_lazy("leave_list")
    login_url = "login"


class LeaveCreateView(LoginRequiredMixin, FormView):
    """Leave Create View."""

    model = Leave
    form_class = LeaveCreateForm
    template_name = "leave_create.html"
    success_url = reverse_lazy("leave_list")
    login_url = "login"

    def form_valid(self, form):
        """Process leave create form."""
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]
        staff_member = form.cleaned_data["staff_member"]
        description = form.cleaned_data["description"]
        dates = [
            start_date + datetime.timedelta(n)
            for n in range(int((end_date - start_date).days + 1))
        ]
        for date in dates:
            Leave.objects.create(
                staff_member=staff_member, description=description, date=date
            )
        return super().form_valid(form)


class RoleListView(LoginRequiredMixin, ListView):
    """Role List View."""

    model = Role
    template_name = "role_list.html"
    login_url = "login"

    def get_queryset(self):
        """Change order of role list view."""
        return Role.objects.order_by("role_name")


class RoleDetailView(LoginRequiredMixin, DetailView):
    """Role Detail View."""

    model = Role
    template_name = "role_detail.html"
    login_url = "login"


class RoleUpdateView(LoginRequiredMixin, UpdateView):
    """Role Update View."""

    model = Role
    fields = ("role_name",)
    template_name = "role_update.html"
    login_url = "login"


class RoleDeleteView(LoginRequiredMixin, DeleteView):
    """Role Delete View."""

    model = Role
    template_name = "role_delete.html"
    success_url = reverse_lazy("role_list")
    login_url = "login"


class RoleCreateView(LoginRequiredMixin, CreateView):
    """Role Create View."""

    model = Role
    template_name = "role_create.html"
    fields = ("role_name",)
    login_url = "login"


class ShiftListView(LoginRequiredMixin, ListView):
    """Shift List View."""

    model = Shift
    template_name = "shift_list.html"
    login_url = "login"


class ShiftDetailView(LoginRequiredMixin, DetailView):
    """Shift Detail View."""

    model = Shift
    template_name = "shift_detail.html"
    login_url = "login"


class ShiftUpdateView(LoginRequiredMixin, UpdateView):
    """Shift Update View."""

    model = Shift
    fields = ("shift_type", "day_group", "max_staff")
    template_name = "shift_edit.html"
    login_url = "login"


class ShiftDeleteView(LoginRequiredMixin, DeleteView):
    """Shift Delete View."""

    model = Shift
    template_name = "shift_delete.html"
    success_url = reverse_lazy("shift_list")
    login_url = "login"


class ShiftCreateView(LoginRequiredMixin, CreateView):
    """Shift Create View."""

    model = Shift
    template_name = "shift_new.html"
    fields = ("shift_type", "day_group", "max_staff")
    login_url = "login"


class ShiftRuleListView(LoginRequiredMixin, ListView):
    """Shift Rule List View."""

    model = ShiftRule
    template_name = "shift_rule_list.html"
    login_url = "login"

    def get_queryset(self):
        """Change order of shift rule list view."""
        return ShiftRule.objects.order_by("shift", "shift_rule_name")


class ShiftRuleDetailView(LoginRequiredMixin, DetailView):
    """Shift Rule Detail View."""

    model = ShiftRule
    template_name = "shift_rule_detail.html"
    login_url = "login"


class ShiftRuleUpdateView(LoginRequiredMixin, UpdateView):
    """Shift Rule Update View."""

    model = ShiftRule
    fields = ("shift_rule_name", "shift")
    template_name = "shift_rule_edit.html"
    login_url = "login"


class ShiftRuleDeleteView(LoginRequiredMixin, DeleteView):
    """Shift Rule Delete View."""

    model = ShiftRule
    template_name = "shift_rule_delete.html"
    success_url = reverse_lazy("shift_rule_list")
    login_url = "login"


class ShiftRuleCreateView(LoginRequiredMixin, CreateView):
    """Shift Rule Create View."""

    model = ShiftRule
    template_name = "shift_rule_new.html"
    fields = ("shift_rule_name", "shift")
    login_url = "login"


class ShiftRuleRoleListView(LoginRequiredMixin, ListView):
    """Shift Rule Role List View."""

    model = ShiftRuleRole
    template_name = "shift_rule_role_list.html"
    login_url = "login"

    def get_queryset(self):
        """Change order of shift rule role list view."""
        return ShiftRuleRole.objects.order_by("shift_rule", "role")


class ShiftRuleRoleDetailView(LoginRequiredMixin, DetailView):
    """Shift Rule Role Detail View."""

    model = ShiftRuleRole
    template_name = "shift_rule_role_detail.html"
    login_url = "login"


class ShiftRuleRoleUpdateView(LoginRequiredMixin, UpdateView):
    """Shift Rule Role Update View."""

    model = ShiftRuleRole
    fields = ("shift_rule", "role", "count")
    template_name = "shift_rule_role_edit.html"
    login_url = "login"


class ShiftRuleRoleDeleteView(LoginRequiredMixin, DeleteView):
    """Shift Rule Role Delete View."""

    model = ShiftRuleRole
    template_name = "shift_rule_role_delete.html"
    success_url = reverse_lazy("shift_rule_list")
    login_url = "login"


class ShiftRuleRoleCreateView(LoginRequiredMixin, CreateView):
    """Shift Rule Role Create View."""

    model = ShiftRuleRole
    template_name = "shift_rule_role_new.html"
    fields = ("role", "count")
    login_url = "login"

    def form_valid(self, form):
        """Process shift rule role create form."""
        shift_rule = get_object_or_404(ShiftRule, id=self.kwargs["shiftrule"])
        form.instance.shift_rule = shift_rule
        return super().form_valid(form)


class StaffRuleListView(LoginRequiredMixin, ListView):
    """Staff Rule List View."""

    model = StaffRule
    template_name = "staff_rule_list.html"
    login_url = "login"

    def get_queryset(self):
        """Change list order."""
        return StaffRule.objects.order_by("staff_rule_name")


class StaffRuleDetailView(LoginRequiredMixin, DetailView):
    """Staff Rule Detail View."""

    model = StaffRule
    template_name = "staff_rule_detail.html"
    login_url = "login"


class StaffRuleUpdateView(LoginRequiredMixin, UpdateView):
    """Staff Rule Update View."""

    model = StaffRule
    form_class = StaffRuleUpdateForm
    template_name = "staff_rule_edit.html"
    login_url = "login"


class StaffRuleDeleteView(LoginRequiredMixin, DeleteView):
    """Staff Rule Delete View."""

    model = StaffRule
    template_name = "staff_rule_delete.html"
    success_url = reverse_lazy("staff_rule_list")
    login_url = "login"


class StaffRuleCreateView(LoginRequiredMixin, CreateView):
    """Staff Rule Create View."""

    model = StaffRule
    form_class = StaffRuleCreateForm
    template_name = "staff_rule_new.html"
    login_url = "login"


class StaffRuleShiftListView(LoginRequiredMixin, ListView):
    """Staff Rule Shift List View."""

    model = StaffRuleShift
    template_name = "staff_rule_shift_list.html"
    login_url = "login"


class StaffRuleShiftDetailView(LoginRequiredMixin, DetailView):
    """Staff Rule Shift Detail View."""

    model = StaffRuleShift
    template_name = "staff_rule_shift_detail.html"
    success_url = reverse_lazy("staff_rule_list")
    login_url = "login"


class StaffRuleShiftUpdateView(LoginRequiredMixin, UpdateView):
    """Staff Rule Shift Update View."""

    model = StaffRuleShift
    fields = ("shift", "position")
    template_name = "staff_rule_shift_edit.html"
    success_url = reverse_lazy("staff_rule_list")
    login_url = "login"


class StaffRuleShiftDeleteView(LoginRequiredMixin, DeleteView):
    """Staff Rule Shift Delete View."""

    model = StaffRuleShift
    template_name = "staff_rule_shift_delete.html"
    success_url = reverse_lazy("staff_rule_list")
    login_url = "login"


class StaffRuleShiftCreateView(LoginRequiredMixin, CreateView):
    """Staff Rule Shift Create View."""

    model = StaffRuleShift
    template_name = "staff_rule_shift_new.html"
    fields = ("shift", "position")
    login_url = "login"

    def form_valid(self, form):
        """Process staff rule shift create form."""
        staff_rule = get_object_or_404(StaffRule, id=self.kwargs["staffrule"])
        form.instance.staff_rule = staff_rule
        return super().form_valid(form)


class TimeSlotListView(LoginRequiredMixin, ListView):
    """Time Slot List View."""

    model = TimeSlot
    template_name = "timeslot_list.html"
    login_url = "login"

    def get_queryset(self):
        """Get timeslots in date range."""
        if "start_date" in self.request.session:
            start_date = datetime.datetime.strptime(
                self.request.session["start_date"], "%d-%b-%Y"
            )
        else:
            start_date = datetime.datetime.now()
        num_days = datetime.timedelta(days=Day.objects.count() - 1)
        end_date = start_date + num_days
        date_range = [start_date, end_date]
        return TimeSlot.objects.filter(date__range=date_range).order_by(
            "date", "shift__shift_type"
        )


class RosterListView(LoginRequiredMixin, ListView):
    """Roster List View."""

    model = TimeSlot
    template_name = "roster_list.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        """Add dates and roster data to context."""
        context = super().get_context_data(**kwargs)
        if "start_date" in self.request.session:
            start_date = datetime.datetime.strptime(
                self.request.session["start_date"], "%d-%b-%Y"
            )
        else:
            start_date = datetime.datetime.now()
        dates, roster = get_roster_by_staff(start_date)
        context["dates"] = dates
        context["roster"] = roster
        return context


class TimeSlotDetailView(LoginRequiredMixin, DetailView):
    """Time Slot Detail View."""

    model = TimeSlot
    template_name = "timeslot_detail.html"
    login_url = "login"


class TimeSlotUpdateView(LoginRequiredMixin, UpdateView):
    """Time Slot Update View."""

    model = TimeSlot
    form_class = TimeSlotUpdateForm
    template_name = "timeslot_edit.html"
    login_url = "login"


class TimeSlotDeleteView(LoginRequiredMixin, DeleteView):
    """Time Slot Delete View."""

    model = TimeSlot
    template_name = "timeslot_delete.html"
    success_url = reverse_lazy("timeslot_list")
    login_url = "login"


class TimeSlotCreateView(LoginRequiredMixin, CreateView):
    """Time Slot Create View."""

    model = TimeSlot
    form_class = TimeSlotCreateForm
    template_name = "timeslot_new.html"
    login_url = "login"


class SelectRosterView(LoginRequiredMixin, FormView):
    """Select Roster View."""

    template_name = "select_roster.html"
    form_class = SelectRosterForm
    success_url = reverse_lazy("timeslot_list")

    def form_valid(self, form):
        """Process select roster form."""
        start_date = form.cleaned_data["start_date"]
        self.request.session["start_date"] = start_date.date().strftime(
            "%d-%b-%Y"
        )
        return super().form_valid(form)


class GenerateRosterView(LoginRequiredMixin, FormView):
    """Generate Roster View."""

    template_name = "generate_roster.html"
    form_class = GenerateRosterForm
    success_url = reverse_lazy("roster_list")

    def form_valid(self, form):
        """Process generate roster form."""
        start_date = form.cleaned_data["start_date"]
        self.request.session["start_date"] = start_date.date().strftime(
            "%d-%b-%Y"
        )
        try:
            roster = RosterGenerator(start_date=start_date)
            roster.create()
        except SolutionNotFeasible:
            messages.error(
                self.request,
                (
                    "Could not generate roster,"
                    " try putting more staff on leave or changing rules."
                ),
            )
        except TooManyStaff:
            messages.error(
                self.request,
                (
                    "There are too many staff available,"
                    " put more staff on leave."
                ),
            )
        return super().form_valid(form)


@login_required
def download_csv(request):
    """Download roster as CSV file."""
    if "start_date" in request.session:
        start_date = datetime.datetime.strptime(
            request.session["start_date"], "%d-%b-%Y"
        )
    else:
        start_date = datetime.datetime.now()

    dates, roster = get_roster_by_staff(start_date)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="roster.csv"'

    writer = csv.writer(response)
    dates = [date.strftime("%a %d-%b-%Y") for date in dates]
    row = ["Staff Member", "Roles", "Shifts"] + dates
    writer.writerow(row)
    for staff_member in roster:
        row = [staff_member]
        for key in roster[staff_member]:
            row.append(roster[staff_member][key])
        writer.writerow(row)
    return response


class DayGroupListView(LoginRequiredMixin, ListView):
    """Day Group List View."""

    model = DayGroup
    template_name = "day_group_list.html"
    login_url = "login"

    def get_queryset(self):
        """Change order of day group list view."""
        return DayGroup.objects.order_by("name")


class DayGroupDetailView(LoginRequiredMixin, DetailView):
    """Day Group Detail View."""

    model = DayGroup
    template_name = "day_group_detail.html"
    login_url = "login"


class DayGroupUpdateView(LoginRequiredMixin, UpdateView):
    """Day Group Update View."""

    model = DayGroup
    fields = ("name",)
    template_name = "day_group_edit.html"
    login_url = "login"


class DayGroupDeleteView(LoginRequiredMixin, DeleteView):
    """Day Group Delete View."""

    model = DayGroup
    template_name = "day_group_delete.html"
    success_url = reverse_lazy("day_group_list")
    login_url = "login"


class DayGroupCreateView(LoginRequiredMixin, CreateView):
    """Day Group Create View."""

    model = DayGroup
    template_name = "day_group_new.html"
    fields = ("name",)
    login_url = "login"

    def form_valid(self, form):
        """Add all days to day group by default."""
        days = Day.objects.all()
        day_group = form.save(commit=False)
        day_group.save()
        for day in days:
            DayGroupDay.objects.get_or_create(day_group=day_group, day=day)
        return super().form_valid(form)


class DayGroupDayListView(LoginRequiredMixin, ListView):
    """Day Group Day List View."""

    model = DayGroupDay
    template_name = "day_group_day_list.html"
    login_url = "login"


class DayGroupDayDetailView(LoginRequiredMixin, DetailView):
    """Day Group Day Detail View."""

    model = DayGroupDay
    template_name = "day_group_day_detail.html"
    success_url = reverse_lazy("day_group_list")
    login_url = "login"


class DayGroupDayUpdateView(LoginRequiredMixin, UpdateView):
    """Day Group Day Update View."""

    model = DayGroupDay
    fields = ("day_group", "day")
    template_name = "day_group_day_edit.html"
    success_url = reverse_lazy("day_group_list")
    login_url = "login"


class DayGroupDayDeleteView(LoginRequiredMixin, DeleteView):
    """Day Group Day Delete View."""

    model = DayGroupDay
    template_name = "day_group_day_delete.html"
    success_url = reverse_lazy("day_group_list")
    login_url = "login"


class DayGroupDayCreateView(LoginRequiredMixin, CreateView):
    """Day Group Day Create View."""

    model = DayGroupDay
    template_name = "day_group_day_new.html"
    fields = ("day",)
    login_url = "login"

    def form_valid(self, form):
        """Process day group day create form."""
        day_group = get_object_or_404(DayGroup, id=self.kwargs["daygroup"])
        form.instance.day_group = day_group
        return super().form_valid(form)


class DayListView(LoginRequiredMixin, ListView):
    """Day List View."""

    model = Day
    template_name = "day_list.html"
    login_url = "login"

    def get_queryset(self):
        """Change order of day list view."""
        return Day.objects.order_by("number")


class DayDetailView(LoginRequiredMixin, DetailView):
    """Day Detail View."""

    model = Day
    template_name = "day_detail.html"
    login_url = "login"


class DayUpdateView(LoginRequiredMixin, UpdateView):
    """Day Update View."""

    model = Day
    fields = ("number",)
    template_name = "day_edit.html"
    login_url = "login"


class DayDeleteView(LoginRequiredMixin, DeleteView):
    """Day Delete View."""

    model = Day
    template_name = "day_delete.html"
    success_url = reverse_lazy("day_list")
    login_url = "login"


class DayCreateView(LoginRequiredMixin, CreateView):
    """Day Create View."""

    model = Day
    template_name = "day_new.html"
    fields = ("number",)
    login_url = "login"


class DaySetCreateView(LoginRequiredMixin, FormView):
    """Day Set Create View."""

    template_name = "day_set_new.html"
    form_class = DaySetCreateForm
    success_url = reverse_lazy("day_list")

    def form_valid(self, form):
        """Process day set create form."""
        number_of_days = form.cleaned_data["number_of_days"]
        for day in range(1, number_of_days + 1):
            Day.objects.get_or_create(number=day)
        actual_number_of_days = Day.objects.count()
        if actual_number_of_days > number_of_days:
            for day in range(number_of_days + 1, actual_number_of_days + 1):
                Day.objects.get(number=day).delete()
        return super().form_valid(form)


class StaffRequestListView(LoginRequiredMixin, ListView):
    """StaffRequest List View."""

    model = StaffRequest
    template_name = "staff_request_list.html"
    login_url = "login"
    context_object_name = "staff_request_list"

    def get_queryset(self):
        """Get staff requests in date range."""
        if "start_date" in self.request.session:
            start_date = datetime.datetime.strptime(
                self.request.session["start_date"], "%d-%b-%Y"
            )
        else:
            start_date = datetime.datetime.now()
        num_days = datetime.timedelta(days=Day.objects.count() - 1)
        end_date = start_date + num_days
        date_range = [start_date, end_date]
        return StaffRequest.objects.filter(date__range=date_range)


class StaffRequestDeleteView(LoginRequiredMixin, DeleteView):
    """StaffRequest Delete View."""

    model = StaffRequest
    template_name = "staff_request_delete.html"
    success_url = reverse_lazy("staff_request_list")
    login_url = "login"
    context_object_name = "staff_request"


class StaffRequestCreateView(LoginRequiredMixin, ListView):
    """Staff Request List View."""

    model = get_user_model()
    template_name = "staff_request_new.html"
    login_url = "login"


class StaffRequestUpdateView(LoginRequiredMixin, FormView):
    """Staff Request Update Form."""

    template_name = "staff_request_edit.html"
    form_class = StaffRequestUpdateForm
    success_url = reverse_lazy("staff_request_list")

    def dispatch(self, request, *args, **kwargs):
        """Collect requests."""
        self.staff_member = get_object_or_404(
            get_user_model(), id=self.kwargs["staffid"]
        )
        if "start_date" in self.request.session:
            start_date = datetime.datetime.strptime(
                self.request.session["start_date"], "%d-%b-%Y"
            )
        else:
            start_date = datetime.datetime.now()
        num_days = datetime.timedelta(days=Day.objects.count() - 1)
        end_date = start_date + num_days
        date_range = [start_date, end_date]
        shift_days = OrderedDict()
        for shift in Shift.objects.all():
            shift_days[shift.shift_type] = []
            for day_group_day in shift.day_group.daygroupday_set.all():
                shift_days[shift.shift_type].append(day_group_day.day.number)
        self.dates = []
        self.shifts = []
        self.requests = []
        self.priorities = []
        staff_requests = StaffRequest.objects.filter(
            staff_member=self.staff_member,
            date__range=date_range
        )
        for day in Day.objects.all():
            for shift in shift_days:
                if day.number in shift_days[shift]:
                    date = start_date + datetime.timedelta(days=day.number - 1)
                    date = date.date()
                    self.dates.append(date)
                    self.shifts.append(shift)
                    # Check for existing staff request here
                    staff_request = staff_requests.filter(
                        date=date,
                        shift__shift_type=shift,
                    ).first()
                    if staff_request is None:
                        self.requests.append("Don't Care")
                        self.priorities.append(1)
                    else:
                        if staff_request.like:
                            self.requests.append("Yes")
                        else:
                            self.requests.append("No")
                        self.priorities.append(staff_request.priority)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add dates and roster data to context."""
        context = super().get_context_data(**kwargs)
        context["staff_member"] = self.staff_member
        context["dates"] = self.dates
        context["shifts"] = self.shifts
        return context

    def form_valid(self, form):
        """Process staff requests form."""
        shifts = Shift.objects.all()
        for i, date in enumerate(self.dates):
            # Delete existing requests for date and shift
            shift = shifts.get(shift_type=self.shifts[i])
            StaffRequest.objects.filter(
                    date=date,
                    shift=shift,
                    staff_member=self.staff_member,
            ).delete()
            if form.cleaned_data[f"request_{i}"] == "Yes":
                StaffRequest.objects.create(
                    date=date,
                    shift=shift,
                    staff_member=self.staff_member,
                    like=True,
                    priority=form.cleaned_data[f"priority_{i}"],
                )
            elif form.cleaned_data[f"request_{i}"] == "No":
                StaffRequest.objects.create(
                    date=date,
                    shift=shift,
                    staff_member=self.staff_member,
                    like=False,
                    priority=form.cleaned_data[f"priority_{i}"],
                )
        return super().form_valid(form)

    def get_form_kwargs(self):
        """Pass number of shifts to form."""
        kwargs = super().get_form_kwargs()
        kwargs["requests"] = self.requests
        kwargs["priorities"] = self.priorities
        return kwargs


class StaffRequestDetailView(LoginRequiredMixin, DetailView):
    """Staff Request Detail View."""

    model = StaffRequest
    template_name = "staff_request_detail.html"
    login_url = "login"
    context_object_name = "staff_request"
