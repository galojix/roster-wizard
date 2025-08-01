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
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.forms import formset_factory

# from django.db import connection, reset_queries

from celery.result import AsyncResult

from .models import (
    Leave,
    Role,
    Shift,
    SkillMixRule,
    SkillMixRuleRole,
    ShiftSequence,
    ShiftSequenceShift,
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
    ShiftSequenceUpdateForm,
    ShiftSequenceCreateForm,
    DaySetCreateForm,
    GenerateRosterForm,
    EditRosterForm,
    SelectRosterForm,
    StaffRequestUpdateForm,
    RosterSettingsForm,
    SelectBulkDeletionPeriodForm,
    ShiftSequenceShiftCreateForm,
)
from .logic import (
    SolutionNotFeasible,
    get_roster_by_staff,
)
from .tasks import generate_roster


class RosterSettingsView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    """Roster Settings View."""

    template_name = "roster_settings.html"
    form_class = RosterSettingsForm
    success_url = reverse_lazy("roster_settings")
    permission_required = "rosters.change_roster"

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
        messages.add_message(
            self.request, messages.SUCCESS, "Settings have been updated..."
        )
        return super().form_valid(form)


class LeaveListView(LoginRequiredMixin, ListView):
    """Leave List View."""

    model = Leave
    template_name = "leave_list.html"

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
        # Users can only see their own leave
        if self.request.user.is_superuser:
            return Leave.objects.filter(date__range=date_range)
        else:
            return Leave.objects.filter(
                date__range=date_range, staff_member=self.request.user
            )


class LeaveDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Leave Detail View."""

    model = Leave
    template_name = "leave_detail.html"

    permission_required = "rosters.change_roster"


class LeaveUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Leave Update View."""

    model = Leave
    form_class = LeaveUpdateForm
    template_name = "leave_update.html"

    permission_required = "rosters.change_roster"


class LeaveDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Leave Delete View."""

    model = Leave
    template_name = "leave_delete.html"
    success_url = reverse_lazy("leave_list")

    permission_required = "rosters.change_roster"


class LeaveCreateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    """Leave Create View."""

    model = Leave
    form_class = LeaveCreateForm
    template_name = "leave_create.html"
    success_url = reverse_lazy("leave_list")

    permission_required = "rosters.change_roster"

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

    def get_queryset(self):
        """Prefetch customuser_set.

        Doing prefetch here as it would not work via a custom model manager.

        """
        return Role.objects.prefetch_related("customuser_set").order_by("role_name")


class RoleDetailView(LoginRequiredMixin, DetailView):
    """Role Detail View."""

    model = Role
    template_name = "role_detail.html"


class RoleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Role Update View."""

    model = Role
    fields = ("role_name",)
    template_name = "role_update.html"

    permission_required = "rosters.change_roster"


class RoleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Role Delete View."""

    model = Role
    template_name = "role_delete.html"
    success_url = reverse_lazy("role_list")

    permission_required = "rosters.change_roster"


class RoleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Role Create View."""

    model = Role
    template_name = "role_create.html"
    fields = ("role_name",)

    permission_required = "rosters.change_roster"


class ShiftListView(LoginRequiredMixin, ListView):
    """Shift List View."""

    model = Shift
    template_name = "shift_list.html"


class ShiftDetailView(LoginRequiredMixin, DetailView):
    """Shift Detail View."""

    model = Shift
    template_name = "shift_detail.html"


class ShiftUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Shift Update View."""

    model = Shift
    fields = ("shift_type", "daygroup")
    template_name = "shift_update.html"

    permission_required = "rosters.change_roster"


class ShiftDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Shift Delete View."""

    model = Shift
    template_name = "shift_delete.html"
    success_url = reverse_lazy("shift_list")

    permission_required = "rosters.change_roster"


class ShiftCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Shift Create View."""

    model = Shift
    template_name = "shift_create.html"
    fields = ("shift_type", "daygroup")

    permission_required = "rosters.change_roster"


class SkillMixRuleListView(LoginRequiredMixin, ListView):
    """Skill Mix Rule List View."""

    model = SkillMixRule
    template_name = "skillmixrule_list.html"

    def get_queryset(self):
        """Change order of shift rule list view."""
        return SkillMixRule.objects.order_by("shift", "skillmixrule_name")


class SkillMixRuleDetailView(LoginRequiredMixin, DetailView):
    """Skill Mix Rule Detail View."""

    model = SkillMixRule
    template_name = "skillmixrule_detail.html"


class SkillMixRuleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Skill Mix Rule Update View."""

    model = SkillMixRule
    fields = ("skillmixrule_name", "shift")
    template_name = "skillmixrule_update.html"

    permission_required = "rosters.change_roster"


class SkillMixRuleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Skill Mix Rule Delete View."""

    model = SkillMixRule
    template_name = "skillmixrule_delete.html"
    success_url = reverse_lazy("skillmixrule_list")

    permission_required = "rosters.change_roster"


class SkillMixRuleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Skill Mix Rule Create View."""

    model = SkillMixRule
    template_name = "skillmixrule_create.html"
    fields = ("skillmixrule_name", "shift")

    permission_required = "rosters.change_roster"


class SkillMixRuleRoleListView(LoginRequiredMixin, ListView):
    """Skill Mix Rule Role List View."""

    model = SkillMixRuleRole
    template_name = "skillmixrulerole_list.html"

    def get_queryset(self):
        """Change order of shift rule role list view."""
        return SkillMixRuleRole.objects.order_by("skillmixrule", "role")


class SkillMixRuleRoleDetailView(LoginRequiredMixin, DetailView):
    """Skill Mix Rule Role Detail View."""

    model = SkillMixRuleRole
    template_name = "skillmixrulerole_detail.html"


class SkillMixRuleRoleUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, UpdateView
):
    """Shift Rule Role Update View."""

    model = SkillMixRuleRole
    fields = ("skillmixrule", "role", "count")
    template_name = "skillmixrulerole_update.html"

    permission_required = "rosters.change_roster"


class SkillMixRuleRoleDeleteView(
    LoginRequiredMixin, PermissionRequiredMixin, DeleteView
):
    """Skill Mix Rule Role Delete View."""

    model = SkillMixRuleRole
    template_name = "skillmixrulerole_delete.html"
    success_url = reverse_lazy("skillmixrule_list")

    permission_required = "rosters.change_roster"


class SkillMixRuleRoleCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, CreateView
):
    """Skill Mix Rule Role Create View."""

    model = SkillMixRuleRole
    template_name = "skillmixrulerole_create.html"
    fields = ("role", "count")

    permission_required = "rosters.change_roster"

    def form_valid(self, form):
        """Process shift rule role create form."""
        skillmixrule = get_object_or_404(SkillMixRule, id=self.kwargs["skillmixrule"])
        form.instance.skillmixrule = skillmixrule
        return super().form_valid(form)


class ShiftSequenceListView(LoginRequiredMixin, ListView):
    """Shift Sequence List View."""

    model = ShiftSequence
    template_name = "shiftsequence_list.html"

    def get_queryset(self):
        """Change list order."""
        return ShiftSequence.objects.order_by("shiftsequence_name")


class ShiftSequenceDetailView(LoginRequiredMixin, DetailView):
    """Shift Sequence Detail View."""

    model = ShiftSequence
    template_name = "shiftsequence_detail.html"


class ShiftSequenceUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Shift Sequence Update View."""

    model = ShiftSequence
    form_class = ShiftSequenceUpdateForm
    template_name = "shiftsequence_update.html"

    permission_required = "rosters.change_roster"


class ShiftSequenceDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Shift Sequence Delete View."""

    model = ShiftSequence
    template_name = "shiftsequence_delete.html"
    success_url = reverse_lazy("shiftsequence_list")

    permission_required = "rosters.change_roster"


class ShiftSequenceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Shift Sequence Create View."""

    model = ShiftSequence
    form_class = ShiftSequenceCreateForm
    template_name = "shiftsequence_create.html"

    permission_required = "rosters.change_roster"


class ShiftSequenceShiftListView(LoginRequiredMixin, ListView):
    """Shift Sequence Shift List View."""

    model = ShiftSequenceShift
    template_name = "shiftsequenceshift_list.html"


class ShiftSequenceShiftDetailView(LoginRequiredMixin, DetailView):
    """Shift Sequence Shift Detail View."""

    model = ShiftSequenceShift
    template_name = "shiftsequenceshift_detail.html"
    success_url = reverse_lazy("shiftsequence_list")


class ShiftSequenceShiftUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, UpdateView
):
    """Shift Sequence Shift Update View."""

    model = ShiftSequenceShift
    fields = ("shift", "position")
    template_name = "shiftsequenceshift_update.html"
    success_url = reverse_lazy("shiftsequence_list")

    permission_required = "rosters.change_roster"


class ShiftSequenceShiftDeleteView(
    LoginRequiredMixin, PermissionRequiredMixin, DeleteView
):
    """Shift Sequence Shift Delete View."""

    model = ShiftSequenceShift
    template_name = "shiftsequenceshift_delete.html"
    success_url = reverse_lazy("shiftsequence_list")

    permission_required = "rosters.change_roster"


class ShiftSequenceShiftCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, CreateView
):
    """Shift Sequence Shift Create View."""

    model = ShiftSequenceShift
    template_name = "shiftsequenceshift_update.html"
    form_class = ShiftSequenceShiftCreateForm
    # fields = ("shift", "position")

    permission_required = "rosters.change_roster"

    def form_valid(self, form):
        """Process staff rule shift create form."""
        shiftsequence = get_object_or_404(
            ShiftSequence, id=self.kwargs["shiftsequence"]
        )
        form.instance.shiftsequence = shiftsequence
        return super().form_valid(form)


class TimeSlotListView(LoginRequiredMixin, ListView):
    """Time Slot List View."""

    model = TimeSlot
    template_name = "timeslot_list.html"

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


class TimeSlotUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Time Slot Update View."""

    model = TimeSlot
    form_class = TimeSlotUpdateForm
    template_name = "timeslot_update.html"

    permission_required = "rosters.change_roster"


class TimeSlotDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Time Slot Delete View."""

    model = TimeSlot
    template_name = "timeslot_delete.html"
    success_url = reverse_lazy("timeslot_list")

    permission_required = "rosters.change_roster"


class TimeSlotCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Time Slot Create View."""

    model = TimeSlot
    form_class = TimeSlotCreateForm
    template_name = "timeslot_create.html"

    permission_required = "rosters.change_roster"


class DayGroupListView(LoginRequiredMixin, ListView):
    """Day Group List View."""

    model = DayGroup
    template_name = "daygroup_list.html"

    def get_queryset(self):
        """Change order of day group list view."""
        return DayGroup.objects.order_by("name")


class DayGroupDetailView(LoginRequiredMixin, DetailView):
    """Day Group Detail View."""

    model = DayGroup
    template_name = "daygroup_detail.html"


class DayGroupUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Day Group Update View."""

    model = DayGroup
    fields = ("name",)
    template_name = "daygroup_update.html"

    permission_required = "rosters.change_roster"


class DayGroupDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Day Group Delete View."""

    model = DayGroup
    template_name = "daygroup_delete.html"
    success_url = reverse_lazy("daygroup_list")

    permission_required = "rosters.change_roster"


class DayGroupCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Day Group Create View."""

    model = DayGroup
    template_name = "daygroup_create.html"
    fields = ("name",)

    permission_required = "rosters.change_roster"

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


class DayGroupDayDetailView(LoginRequiredMixin, DetailView):
    """Day Group Day Detail View."""

    model = DayGroupDay
    template_name = "daygroupday_detail.html"
    success_url = reverse_lazy("daygroup_list")


class DayGroupDayUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Day Group Day Update View."""

    model = DayGroupDay
    fields = ("daygroup", "day")
    template_name = "daygroupday_update.html"
    success_url = reverse_lazy("daygroup_list")

    permission_required = "rosters.change_roster"


class DayGroupDayDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Day Group Day Delete View."""

    model = DayGroupDay
    template_name = "daygroupday_delete.html"
    success_url = reverse_lazy("daygroup_list")

    permission_required = "rosters.change_roster"


class DayGroupDayCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Day Group Day Create View."""

    model = DayGroupDay
    template_name = "daygroupday_create.html"
    form_class = DayGroupDayCreateForm

    permission_required = "rosters.change_roster"

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

    def get_queryset(self):
        """Change order of day list view."""
        return Day.objects.order_by("number")


class DayDetailView(LoginRequiredMixin, DetailView):
    """Day Detail View."""

    model = Day
    template_name = "day_detail.html"


class DayUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Day Update View."""

    model = Day
    fields = ("number",)
    template_name = "day_update.html"

    permission_required = "rosters.change_roster"


class DayDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Day Delete View."""

    model = Day
    template_name = "day_delete.html"
    success_url = reverse_lazy("day_list")

    permission_required = "rosters.change_roster"


class DayCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Day Create View."""

    model = Day
    template_name = "day_create.html"
    fields = ("number",)

    permission_required = "rosters.change_roster"


class DaySetCreateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    """Day Set Create View."""

    template_name = "day_set_create.html"
    form_class = DaySetCreateForm
    success_url = reverse_lazy("day_list")
    permission_required = "rosters.change_roster"

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
        # Users can only see their own requests
        if self.request.user.is_superuser:
            return StaffRequest.objects.filter(date__range=date_range)
        else:
            return StaffRequest.objects.filter(
                date__range=date_range, staff_member=self.request.user
            )


class StaffRequestDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """StaffRequest Delete View."""

    model = StaffRequest
    template_name = "staffrequest_delete.html"
    success_url = reverse_lazy("staffrequest_list")

    permission_required = "rosters.change_roster"


class StaffRequestCreateView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Staff Request List View."""

    model = get_user_model()
    template_name = "staffrequest_create.html"

    permission_required = "rosters.change_roster"


class StaffRequestUpdateView(LoginRequiredMixin, FormView):
    """Staff Request Update Form."""

    template_name = "staffrequest_update.html"
    form_class = StaffRequestUpdateForm
    success_url = reverse_lazy("staffrequest_list")

    def __init__(self):
        """Initialize StaffRequestUpdateView."""
        super().__init__()
        self.staff_member = None
        self.dates = []
        self.shifts = []
        self.requests = []
        self.priorities = []

    def dispatch(self, request, *args, **kwargs):
        """Collect requests."""
        self.staff_member = get_object_or_404(
            get_user_model(), id=self.kwargs["staffid"]
        )
        # Make sure users can only update their own requests
        if (
            not self.request.user.is_superuser
            and self.request.user != self.staff_member
        ):
            self.staff_member = self.request.user
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
            daygroup: list(daygroup.shift_set.all())
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
                date = (start_date + datetime.timedelta(days=day.number - 1)).date()
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
        """Pass number request and priorities to form."""
        kwargs = super().get_form_kwargs()
        kwargs["requests"] = self.requests
        kwargs["priorities"] = self.priorities
        return kwargs


class StaffRequestDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Staff Request Detail View."""

    model = StaffRequest
    template_name = "staffrequest_detail.html"

    permission_required = "rosters.change_roster"


class RosterByStaffView(LoginRequiredMixin, TemplateView):
    """Roster By Staff View."""

    template_name = "roster_by_staff.html"

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
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        """Process select roster form."""
        start_date = form.cleaned_data["start_date"]
        self.request.session["start_date"] = start_date.date().strftime("%d-%b-%Y")
        return super().form_valid(form)


class SelectBulkDeletionPeriodView(
    LoginRequiredMixin, PermissionRequiredMixin, FormView
):
    """Select Bulk Deletion Period View."""

    template_name = "select_bulk_deletion_period.html"
    form_class = SelectBulkDeletionPeriodForm
    success_url = reverse_lazy("roster_by_staff")
    permission_required = "rosters.change_roster"

    def form_valid(self, form):
        """Process bulk deltion period form."""
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]
        date_range = [start_date, end_date]
        timeslots = TimeSlot.objects.filter(date__range=date_range)
        timeslots.delete()
        return super().form_valid(form)


class GenerateRosterView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    """Generate Roster View."""

    template_name = "generate_roster.html"
    form_class = GenerateRosterForm
    permission_required = "rosters.change_roster"
    success_url = reverse_lazy("generate_roster")

    def get_form_kwargs(self):
        """Pass request to form."""
        kwargs = super().get_form_kwargs()
        kwargs.update(request=self.request)
        return kwargs

    def form_valid(self, form):
        """Process generate roster form."""
        start_date = form.cleaned_data["start_date"]
        self.request.session["start_date"] = start_date.date().strftime("%d-%b-%Y")
        if "task_id" in self.request.session:
            task = AsyncResult(self.request.session["task_id"])
            if not task.ready():
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    "Roster generation is already in progress...",
                )
                return render(self.request, "generate_roster.html", {"form": form})
        try:
            result = generate_roster.delay(start_date=start_date)
        except Exception as error:  # pylint: disable=broad-exception-caught
            messages.add_message(
                self.request,
                messages.ERROR,
                f"Error: {error}, Please try again...",
            )
            return HttpResponseRedirect(reverse("generate_roster"))
        self.request.session["task_id"] = result.task_id
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Roster is generating, see menu bar for status...",
        )
        return super().form_valid(form)


@login_required
@permission_required("rosters.change_roster")
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
    staff_ids = [staff_member.id for staff_member in staff_members]

    # Create timeslots if they do not already exist
    for shift in Shift.objects.all():
        daygroupdays = shift.daygroup.daygroupday_set.all()
        for daygroupday in daygroupdays:
            if not TimeSlot.objects.filter(
                date=dates[daygroupday.day.number - 1], shift=shift
            ).exists():
                TimeSlot.objects.create(
                    date=dates[daygroupday.day.number - 1], shift=shift
                )

    EditRosterFormSet = formset_factory(EditRosterForm, extra=0)

    date_range = [
        start_date.date(),
        start_date.date() + datetime.timedelta(days=num_days - 1),
    ]

    all_timeslots = TimeSlot.objects.filter(date__range=date_range)

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
                dates, all_timeslots, formset, start_date, staff_ids
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
    EditRosterFormSet,  # pylint: disable=invalid-name
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
            shift_types_lookup[staff_member.id][timeslot.date] = (
                timeslot.shift.shift_type
            )

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


def process_edit_roster_form(dates, all_timeslots, formset, start_date, staff_ids):
    """Process edit roster form."""
    # Cleaned data from formset is a list of dictionaries
    timeslots_lookup = {date: [] for date in dates}
    for timeslot in all_timeslots:
        timeslots_lookup[timeslot.date].append(timeslot)

    # Clear staff from all timeslots
    for timeslot in all_timeslots:
        timeslot.staff.clear()

    # Populate timeslots with staff as per form
    TimeSlotStaffRelationship = TimeSlot.staff.through  # pylint: disable=invalid-name
    staff_to_add = []
    for staff_num, shift_set in enumerate(formset.cleaned_data):
        for day_num, day_label in enumerate(shift_set):
            shift_type = shift_set[day_label]
            timeslots = timeslots_lookup[
                (start_date + datetime.timedelta(days=day_num)).date()
            ]
            for timeslot in timeslots:
                if timeslot.shift.shift_type == shift_type:
                    staff_to_add.append(
                        TimeSlotStaffRelationship(
                            timeslot_id=timeslot.id,
                            customuser_id=staff_ids[staff_num],
                        )
                    )
    TimeSlotStaffRelationship.objects.bulk_create(staff_to_add)


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
        row.extend(roster[staff_member][key] for key in roster[staff_member])
        writer.writerow(row)
    return response


@login_required
@permission_required("rosters.change_roster")
def staff_request_status(request):
    """Display staff request status."""
    print("starting")
    if "start_date" in request.session:
        start_date = datetime.datetime.strptime(
            request.session["start_date"], "%d-%b-%Y"
        )
    else:
        start_date = datetime.datetime.now()

    num_days = datetime.timedelta(days=Day.objects.count() - 1)
    end_date = start_date + num_days
    date_range = [start_date, end_date]

    staff_requests = StaffRequest.objects.filter(date__range=date_range)
    timeslots = TimeSlot.objects.filter(date__range=date_range)
    successes = []
    failures = []
    for staff_request in staff_requests:
        date = staff_request.date
        shift = staff_request.shift
        staff_member = staff_request.staff_member
        like = staff_request.like
        if like:
            if staff_member in timeslots.get(date=date, shift=shift).staff.all():
                successes.append(f"{staff_member} given {shift} on {date}")
            else:
                failures.append(f"{staff_member} not given {shift} on {date}")
        else:
            if staff_member in timeslots.get(date=date, shift=shift).staff.all():
                failures.append(f"{staff_member} given {shift} on {date}")
            else:
                successes.append(f"{staff_member} not given {shift} on {date}")

    return render(
        request,
        "staff_request_status.html",
        {
            "successes": successes,
            "failures": failures,
        },
    )


@login_required
@permission_required("rosters.change_roster")
def roster_status_indicator(request):
    """Indicate roster status."""
    if not request.session["task_id"]:
        return HttpResponse(
            "<button class='btn btn-warning' id='roster-status'>Roster: Not Started</button>"
        )
    task = AsyncResult(request.session["task_id"])
    if task.ready():
        return render(
            request, "roster_ready.html", {"task_id": request.session["task_id"]}
        )
    else:
        return HttpResponse(
            "<button class='btn btn-warning' id='roster-status'>Roster: Processing</button>"
        )


@login_required
@permission_required("rosters.change_roster")
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
            status_message = (
                "Could not generate roster, "
                "ensure staff details and rules are correct..."
            )
        except Exception as error:  # pylint: disable=broad-exception-caught
            status = "FAILED"
            if "no attribute 'daygroupday_set'" in str(error):
                status_message = (
                    "Please check that all shifts and "
                    "shift sequences have day groups assigned..."
                )
            else:
                status_message = f"{error.__class__.__name__}:{error}"
    else:
        status = "PROCESSING"
        status_message = "Processing..."
    return render(
        request,
        "roster_generation_status.html",
        {"status_message": status_message, "status": status},
    )
