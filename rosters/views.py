"""Views."""

import datetime
import csv

from collections import namedtuple

from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import (
    UpdateView,
    DeleteView,
    CreateView,
    FormView,
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.forms import formset_factory

# from django.db.models.query import prefetch_related_objects


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
    RosterSettings,
)
from .forms import (
    DayGroupDayCreateForm,
    LeaveCreateForm,
    LeaveUpdateForm,
    TimeSlotUpdateForm,
    TimeSlotCreateForm,
    StaffRuleUpdateForm,
    StaffRuleCreateForm,
    DaySetCreateForm,
    GenerateRosterForm,
    EditRosterForm,
    SelectRosterForm,
    StaffRequestUpdateForm,
    RosterSettingsForm,
    SelectBulkDeletionPeriodForm,
)
from .logic import (
    SolutionNotFeasible,
    TooManyStaff,
    get_roster_by_staff,
)
from .tasks import generate_roster
from celery.result import AsyncResult


class RosterSettingsView(LoginRequiredMixin, FormView):
    """Roster Settings View."""

    template_name = "roster_settings.html"
    form_class = RosterSettingsForm
    success_url = reverse_lazy("roster_settings")

    def get_form_kwargs(self):
        """Pass current settings to form."""
        kwargs = super().get_form_kwargs()
        if RosterSettings.objects.exists():
            kwargs["roster_name"] = RosterSettings.objects.first().roster_name
            kwargs["not_used"] = RosterSettings.objects.first().not_used
        else:
            kwargs["roster_name"] = "No Roster Name Set"
            kwargs["not_used"] = "not_used"
        return kwargs

    def form_valid(self, form):
        """Process roster settings form."""
        roster_name = form.cleaned_data["roster_name"]
        not_used = form.cleaned_data["not_used"]
        if RosterSettings.objects.exists():
            new_settings = RosterSettings.objects.first()
            new_settings.roster_name = roster_name
            new_settings.not_used = not_used
        else:
            new_settings = RosterSettings.objects.create(
                roster_name=roster_name, not_used=not_used
            )
        new_settings.save()
        # messages.set_level(self.request, messages.DEBUG)
        messages.add_message(
            self.request, messages.SUCCESS, "Settings have been updated..."
        )
        return super().form_valid(form)


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
    fields = ("shift_type", "daygroup", "max_staff")
    template_name = "shift_update.html"
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
    template_name = "shift_create.html"
    fields = ("shift_type", "daygroup", "max_staff")
    login_url = "login"


class ShiftRuleListView(LoginRequiredMixin, ListView):
    """Shift Rule List View."""

    model = ShiftRule
    template_name = "shiftrule_list.html"
    login_url = "login"

    def get_queryset(self):
        """Change order of shift rule list view."""
        return ShiftRule.objects.order_by("shift", "shiftrule_name")


class ShiftRuleDetailView(LoginRequiredMixin, DetailView):
    """Shift Rule Detail View."""

    model = ShiftRule
    template_name = "shiftrule_detail.html"
    login_url = "login"


class ShiftRuleUpdateView(LoginRequiredMixin, UpdateView):
    """Shift Rule Update View."""

    model = ShiftRule
    fields = ("shiftrule_name", "shift")
    template_name = "shiftrule_update.html"
    login_url = "login"


class ShiftRuleDeleteView(LoginRequiredMixin, DeleteView):
    """Shift Rule Delete View."""

    model = ShiftRule
    template_name = "shiftrule_delete.html"
    success_url = reverse_lazy("shiftrule_list")
    login_url = "login"


class ShiftRuleCreateView(LoginRequiredMixin, CreateView):
    """Shift Rule Create View."""

    model = ShiftRule
    template_name = "shiftrule_create.html"
    fields = ("shiftrule_name", "shift")
    login_url = "login"


class ShiftRuleRoleListView(LoginRequiredMixin, ListView):
    """Shift Rule Role List View."""

    model = ShiftRuleRole
    template_name = "shiftrulerole_list.html"
    login_url = "login"

    def get_queryset(self):
        """Change order of shift rule role list view."""
        return ShiftRuleRole.objects.order_by("shiftrule", "role")


class ShiftRuleRoleDetailView(LoginRequiredMixin, DetailView):
    """Shift Rule Role Detail View."""

    model = ShiftRuleRole
    template_name = "shiftrulerole_detail.html"
    login_url = "login"


class ShiftRuleRoleUpdateView(LoginRequiredMixin, UpdateView):
    """Shift Rule Role Update View."""

    model = ShiftRuleRole
    fields = ("shiftrule", "role", "count")
    template_name = "shiftrulerole_update.html"
    login_url = "login"


class ShiftRuleRoleDeleteView(LoginRequiredMixin, DeleteView):
    """Shift Rule Role Delete View."""

    model = ShiftRuleRole
    template_name = "shiftrulerole_delete.html"
    success_url = reverse_lazy("shiftrule_list")
    login_url = "login"


class ShiftRuleRoleCreateView(LoginRequiredMixin, CreateView):
    """Shift Rule Role Create View."""

    model = ShiftRuleRole
    template_name = "shiftrulerole_create.html"
    fields = ("role", "count")
    login_url = "login"

    def form_valid(self, form):
        """Process shift rule role create form."""
        shiftrule = get_object_or_404(ShiftRule, id=self.kwargs["shiftrule"])
        form.instance.shiftrule = shiftrule
        return super().form_valid(form)


class StaffRuleListView(LoginRequiredMixin, ListView):
    """Staff Rule List View."""

    model = StaffRule
    template_name = "staffrule_list.html"
    login_url = "login"

    def get_queryset(self):
        """Change list order."""
        return StaffRule.objects.order_by("staffrule_name")


class StaffRuleDetailView(LoginRequiredMixin, DetailView):
    """Staff Rule Detail View."""

    model = StaffRule
    template_name = "staffrule_detail.html"
    login_url = "login"


class StaffRuleUpdateView(LoginRequiredMixin, UpdateView):
    """Staff Rule Update View."""

    model = StaffRule
    form_class = StaffRuleUpdateForm
    template_name = "staffrule_update.html"
    login_url = "login"


class StaffRuleDeleteView(LoginRequiredMixin, DeleteView):
    """Staff Rule Delete View."""

    model = StaffRule
    template_name = "staffrule_delete.html"
    success_url = reverse_lazy("staffrule_list")
    login_url = "login"


class StaffRuleCreateView(LoginRequiredMixin, CreateView):
    """Staff Rule Create View."""

    model = StaffRule
    form_class = StaffRuleCreateForm
    template_name = "staffrule_create.html"
    login_url = "login"


class StaffRuleShiftListView(LoginRequiredMixin, ListView):
    """Staff Rule Shift List View."""

    model = StaffRuleShift
    template_name = "staffruleshift_list.html"
    login_url = "login"


class StaffRuleShiftDetailView(LoginRequiredMixin, DetailView):
    """Staff Rule Shift Detail View."""

    model = StaffRuleShift
    template_name = "staffruleshift_detail.html"
    success_url = reverse_lazy("staffrule_list")
    login_url = "login"


class StaffRuleShiftUpdateView(LoginRequiredMixin, UpdateView):
    """Staff Rule Shift Update View."""

    model = StaffRuleShift
    fields = ("shift", "position")
    template_name = "staffruleshift_update.html"
    success_url = reverse_lazy("staffrule_list")
    login_url = "login"


class StaffRuleShiftDeleteView(LoginRequiredMixin, DeleteView):
    """Staff Rule Shift Delete View."""

    model = StaffRuleShift
    template_name = "staffruleshift_delete.html"
    success_url = reverse_lazy("staffrule_list")
    login_url = "login"


class StaffRuleShiftCreateView(LoginRequiredMixin, CreateView):
    """Staff Rule Shift Create View."""

    model = StaffRuleShift
    template_name = "staffruleshift_create.html"
    fields = ("shift", "position")
    login_url = "login"

    def form_valid(self, form):
        """Process staff rule shift create form."""
        staffrule = get_object_or_404(StaffRule, id=self.kwargs["staffrule"])
        form.instance.staffrule = staffrule
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
        return (
            TimeSlot.objects.filter(date__range=date_range)
            .order_by("date", "shift__shift_type")
            .prefetch_related("staff__roles")
        )


class TimeSlotDetailView(LoginRequiredMixin, DetailView):
    """Time Slot Detail View."""

    model = TimeSlot
    template_name = "timeslot_detail.html"
    login_url = "login"


class TimeSlotUpdateView(LoginRequiredMixin, UpdateView):
    """Time Slot Update View."""

    model = TimeSlot
    form_class = TimeSlotUpdateForm
    template_name = "timeslot_update.html"
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
    template_name = "timeslot_create.html"
    login_url = "login"


class DayGroupListView(LoginRequiredMixin, ListView):
    """Day Group List View."""

    model = DayGroup
    template_name = "daygroup_list.html"
    login_url = "login"

    def get_queryset(self):
        """Change order of day group list view."""
        return DayGroup.objects.order_by("name")


class DayGroupDetailView(LoginRequiredMixin, DetailView):
    """Day Group Detail View."""

    model = DayGroup
    template_name = "daygroup_detail.html"
    login_url = "login"


class DayGroupUpdateView(LoginRequiredMixin, UpdateView):
    """Day Group Update View."""

    model = DayGroup
    fields = ("name",)
    template_name = "daygroup_update.html"
    login_url = "login"


class DayGroupDeleteView(LoginRequiredMixin, DeleteView):
    """Day Group Delete View."""

    model = DayGroup
    template_name = "daygroup_delete.html"
    success_url = reverse_lazy("daygroup_list")
    login_url = "login"


class DayGroupCreateView(LoginRequiredMixin, CreateView):
    """Day Group Create View."""

    model = DayGroup
    template_name = "daygroup_create.html"
    fields = ("name",)
    login_url = "login"

    def form_valid(self, form):
        """Add all days to day group by default."""
        days = Day.objects.all()
        daygroup = form.save(commit=False)
        daygroup.save()
        for day in days:
            DayGroupDay.objects.get_or_create(daygroup=daygroup, day=day)
        return super().form_valid(form)


class DayGroupDayListView(LoginRequiredMixin, ListView):
    """Day Group Day List View."""

    model = DayGroupDay
    template_name = "daygroupday_list.html"
    login_url = "login"


class DayGroupDayDetailView(LoginRequiredMixin, DetailView):
    """Day Group Day Detail View."""

    model = DayGroupDay
    template_name = "daygroupday_detail.html"
    success_url = reverse_lazy("daygroup_list")
    login_url = "login"


class DayGroupDayUpdateView(LoginRequiredMixin, UpdateView):
    """Day Group Day Update View."""

    model = DayGroupDay
    fields = ("daygroup", "day")
    template_name = "daygroupday_update.html"
    success_url = reverse_lazy("daygroup_list")
    login_url = "login"


class DayGroupDayDeleteView(LoginRequiredMixin, DeleteView):
    """Day Group Day Delete View."""

    model = DayGroupDay
    template_name = "daygroupday_delete.html"
    success_url = reverse_lazy("daygroup_list")
    login_url = "login"


class DayGroupDayCreateView(LoginRequiredMixin, CreateView):
    """Day Group Day Create View."""

    model = DayGroupDay
    template_name = "daygroupday_create.html"
    form_class = DayGroupDayCreateForm
    login_url = "login"

    def form_valid(self, form):
        """Process day group day create form."""
        daygroup = get_object_or_404(DayGroup, id=self.kwargs["daygroup"])
        form.instance.daygroup = daygroup
        return super().form_valid(form)

    def get_form_kwargs(self):
        """Pass daygroup to form."""
        kwargs = super().get_form_kwargs()
        kwargs["daygroup"] = self.kwargs["daygroup"]
        return kwargs


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
    template_name = "day_update.html"
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
    template_name = "day_create.html"
    fields = ("number",)
    login_url = "login"


class DaySetCreateView(LoginRequiredMixin, FormView):
    """Day Set Create View."""

    template_name = "day_set_create.html"
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
    template_name = "staffrequest_list.html"
    login_url = "login"

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
    template_name = "staffrequest_delete.html"
    success_url = reverse_lazy("staffrequest_list")
    login_url = "login"


class StaffRequestCreateView(LoginRequiredMixin, ListView):
    """Staff Request List View."""

    model = get_user_model()
    template_name = "staffrequest_create.html"
    login_url = "login"


class StaffRequestUpdateView(LoginRequiredMixin, FormView):
    """Staff Request Update Form."""

    template_name = "staffrequest_update.html"
    form_class = StaffRequestUpdateForm
    success_url = reverse_lazy("staffrequest_list")

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
        self.dates = []
        self.shifts = []
        self.requests = []
        self.priorities = []
        staffrequests = StaffRequest.objects.filter(
            date__range=date_range, staff_member=self.staff_member
        )
        RequestDetail = namedtuple("RequestDetail", "like priority")
        request_lookup = {
            (staffrequest.date, staffrequest.shift): RequestDetail(
                like=staffrequest.like,
                priority=staffrequest.priority,
            )
            for staffrequest in staffrequests
        }
        daygroup_shifts_map = {
            daygroup: [shift for shift in daygroup.shift_set.all()]
            for daygroup in DayGroup.objects.all()
        }
        day_shifts_map = {}
        days = Day.objects.all()
        for day in days:
            day_shifts_map[day.number] = []
            for daygroupday in day.daygroupday_set.all():
                for shift in daygroup_shifts_map[daygroupday.daygroup]:
                    day_shifts_map[day.number].append(shift)
        for day in days:
            for shift in day_shifts_map[day.number]:
                date = (
                    start_date + datetime.timedelta(days=(day.number - 1))
                ).date()
                self.dates.append(date)
                self.shifts.append(shift)
                request_id = (date, shift)
                if request_id in request_lookup:
                    if request_lookup[request_id].like:
                        self.requests.append("Yes")
                    else:
                        self.requests.append("No")
                    self.priorities.append(request_lookup[request_id].priority)
                else:
                    self.requests.append("Don't Care")
                    self.priorities.append(1)
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
    template_name = "staffrequest_detail.html"
    login_url = "login"


class RosterByStaffView(LoginRequiredMixin, TemplateView):
    """Roster By Staff View."""

    template_name = "roster_by_staff.html"
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


class SelectRosterPeriodView(LoginRequiredMixin, FormView):
    """Select Roster Period View."""

    template_name = "select_roster_period.html"
    form_class = SelectRosterForm
    success_url = reverse_lazy("roster_by_staff")

    def form_valid(self, form):
        """Process select roster form."""
        start_date = form.cleaned_data["start_date"]
        self.request.session["start_date"] = start_date.date().strftime(
            "%d-%b-%Y"
        )
        return super().form_valid(form)


class SelectBulkDeletionPeriodView(LoginRequiredMixin, FormView):
    """Select Bulk Deletion Period View."""

    template_name = "select_bulk_deletion_period.html"
    form_class = SelectBulkDeletionPeriodForm
    success_url = reverse_lazy("roster_by_staff")

    def form_valid(self, form):
        """Process bulk deltion period form."""
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]
        date_range = [start_date, end_date]
        timeslots = TimeSlot.objects.filter(date__range=date_range)
        timeslots.delete()
        return super().form_valid(form)


class GenerateRosterView(LoginRequiredMixin, FormView):
    """Generate Roster View."""

    template_name = "generate_roster.html"
    form_class = GenerateRosterForm

    def get_form_kwargs(self):
        """Pass request to form."""
        kwargs = super().get_form_kwargs()
        kwargs.update(request=self.request)
        return kwargs

    def get_success_url(self):
        """Get success URL."""
        return reverse("roster_generation_status", args=(self.task_id,))

    def form_valid(self, form):
        """Process generate roster form."""
        start_date = form.cleaned_data["start_date"]
        self.request.session["start_date"] = start_date.date().strftime(
            "%d-%b-%Y"
        )
        result = generate_roster.delay(start_date=start_date)
        self.task_id = result.task_id
        return super().form_valid(form)


@login_required
def edit_roster(request):
    """Edit Roster View."""
    if "start_date" in request.session:
        start_date = datetime.datetime.strptime(
            request.session["start_date"], "%d-%b-%Y"
        )
    else:
        start_date = datetime.datetime.now()

    num_days = Day.objects.count()

    dates = [
        (start_date + datetime.timedelta(days=day_num)).date()
        for day_num in range(num_days)
    ]

    staff_members = get_user_model().objects.all()

    # Create timeslots if they do not already exist
    for shift in Shift.objects.all():
        daygroupdays = shift.daygroup.daygroupday_set.all()
        for daygroupday in daygroupdays:
            TimeSlot.objects.get_or_create(
                date=dates[daygroupday.day.number - 1], shift=shift
            )

    EditRosterFormSet = formset_factory(EditRosterForm, extra=0)

    date_range = [
        start_date.date(),
        start_date.date() + datetime.timedelta(days=num_days - 1),
    ]

    all_timeslots = TimeSlot.objects.filter(date__range=date_range)
    # print(all_timeslots)

    shift_types = [shift.shift_type for shift in Shift.objects.all()]
    shift_types.append("X")

    # Form posted
    if request.method == "POST":
        formset = EditRosterFormSet(
            request.POST,
            form_kwargs={"shift_types": shift_types, "num_days": num_days},
        )
        if formset.is_valid():
            process_edit_roster_form(
                dates, all_timeslots, formset, start_date, staff_members
            )
            return HttpResponseRedirect(reverse("roster_by_staff"))
    # Form not posted
    else:
        formset = populate_edit_roster_form(
            staff_members,
            all_timeslots,
            EditRosterFormSet,
            dates,
            shift_types,
            num_days,
        )

    return render(
        request,
        "edit_roster.html",
        {
            "formset": formset,
            "staff_members": staff_members,
            "dates": dates,
        },
    )


def populate_edit_roster_form(
    staff_members,
    all_timeslots,
    EditRosterFormSet,
    dates,
    shift_types,
    num_days,
):
    """Populate edit roster form."""
    # Create lookup for shift type from staff_member and date
    shift_types_lookup = {
        staff_member.id: {timeslot.date: "X" for timeslot in all_timeslots}
        for staff_member in staff_members
    }

    for timeslot in all_timeslots:
        for staff_member in timeslot.staff.all():
            shift_types_lookup[staff_member.id][
                timeslot.date
            ] = timeslot.shift.shift_type
    # Populate formset with existing data
    initial = []
    for staff_member in staff_members:
        staff_shifts = {}
        for day_num, date in enumerate(dates):
            shift_type = shift_types_lookup[staff_member.id][date]
            staff_shifts["day-" + str(day_num)] = shift_type
        initial.append(staff_shifts)
    return EditRosterFormSet(
        initial=initial,
        form_kwargs={"shift_types": shift_types, "num_days": num_days},
    )


def process_edit_roster_form(
    dates, all_timeslots, formset, start_date, staff_members
):
    """Process edit roster form."""
    # Cleaned data from formset is a list of dictionaries
    timeslots_lookup = {date: [] for date in dates}
    for timeslot in all_timeslots:
        timeslots_lookup[timeslot.date].append(timeslot)

    staff_lookup = {
        timeslot: timeslot.staff.all() for timeslot in all_timeslots
    }
    for staff_num, shift_set in enumerate(formset.cleaned_data):
        for day_num, day_label in enumerate(shift_set):
            shift_type = shift_set[day_label]
            timeslots = timeslots_lookup[
                (start_date + datetime.timedelta(days=day_num)).date()
            ]
            for timeslot in timeslots:
                if timeslot.shift.shift_type == shift_type:
                    if staff_members[staff_num] not in staff_lookup[timeslot]:
                        timeslot.staff.add(staff_members[staff_num])
                else:
                    if staff_members[staff_num] in staff_lookup[timeslot]:
                        timeslot.staff.remove(staff_members[staff_num])


@login_required
def roster_generation_status(request, task_id):
    """Display roster generation status."""
    task = AsyncResult(task_id)
    status = "PROCESSING"
    if task.ready():
        try:
            status_message = task.get()
            status = "SUCCEEDED"
        except SolutionNotFeasible:
            status = "FAILED"
            status_message = "Could not generate roster, try putting more staff on leave or changing rules..."
        except TooManyStaff:
            status = "FAILED"
            status_message = "There are too many staff available, put more staff on leave..."
    else:
        status = "PROCESSING"
        status_message = "Processing..."
    return render(
        request,
        "roster_generation_status.html",
        {"status_message": status_message, "status": status},
    )


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
