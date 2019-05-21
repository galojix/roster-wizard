from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin

# from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from ortools.sat.python import cp_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import datetime


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
)


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
    fields = ("role_name", "staff")
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


class StaffRuleDetailView(LoginRequiredMixin, DetailView):
    model = StaffRule
    template_name = "staff_rule_detail.html"
    login_url = "login"


class StaffRuleUpdateView(LoginRequiredMixin, UpdateView):
    model = StaffRule
    fields = ("staff_rule_name", "staff")
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
    fields = ("staff_rule_name",)
    login_url = "login"


class StaffRuleShiftListView(LoginRequiredMixin, ListView):
    model = StaffRuleShift
    template_name = "staff_rule_shift_list.html"
    login_url = "login"


class StaffRuleShiftDetailView(LoginRequiredMixin, DetailView):
    model = StaffRuleShift
    template_name = "staff_rule_shift_detail.html"
    login_url = "login"


class StaffRuleShiftUpdateView(LoginRequiredMixin, UpdateView):
    model = StaffRuleShift
    fields = ("shift", "position")
    template_name = "staff_rule_shift_edit.html"
    login_url = "login"


class StaffRuleShiftDeleteView(LoginRequiredMixin, DeleteView):
    model = StaffRuleShift
    template_name = "staff_rule_shift_delete.html"
    success_url = reverse_lazy("staff_rule_shift_list")
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
        return TimeSlot.objects.order_by("date", "shift__shift_type")


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


@login_required
def generate_roster(request):

    nurses = get_user_model().objects.all()
    shifts = Shift.objects.all().order_by("shift_type")
    num_days = 14

    # Create dates and timeslots
    TimeSlot.objects.all().delete()
    dates = []
    date = datetime.date.today()
    for day in range(num_days):
        dates.append(date)
        for shift in shifts:
            TimeSlot.objects.create(date=date, shift=shift)
        date += datetime.timedelta(days=1)
    timeslots = TimeSlot.objects.all()

    # Create shift requests
    shift_requests = []
    for nurse in nurses:
        nurse_shift_requests = []
        preferences = nurse.preference_set.all()
        for day in range(num_days):
            nurse_shift_requests_for_day = []
            for shift in shifts:
                priority = 0
                for preference in preferences:
                    if preference.day == day and preference.shift == shift:
                        priority = preference.priority
                nurse_shift_requests_for_day.append(priority)
            nurse_shift_requests.append(nurse_shift_requests_for_day)
        shift_requests.append(nurse_shift_requests)

    # Create the model
    model = cp_model.CpModel()

    # Create shift variables
    # shifts[(n, r, d, t)]:
    # nurse 'n' with role 'r' works on date 'd' in timeslot 't'
    shift_vars = {}
    for nurse in nurses:
        for role in nurse.roles.all():
            for date in dates:
                for timeslot in TimeSlot.objects.filter(date=date).order_by(
                    "shift__shift_type"
                ):
                    n = nurse.id
                    r = role.id
                    d = date
                    t = timeslot.id
                    shift_vars[(n, r, d, t)] = model.NewBoolVar(
                        f"shift_n{n}r{r}d{d}t{t}"
                    )

    # Assign each shift to exactly 5 nurses
    # for timeslot in timeslots:
    #     t = timeslot.id
    #     model.Add(
    #         sum(
    #             shift_vars[(nurse.id, role.id, timeslot.date, t)]
    #             for nurse in nurses
    #             for role in nurse.roles.all()
    #         )
    #         == 5
    #     )

    # Collect shift rules into friendly structure
    shift_rules = {}
    for shift in shifts:
        shift_rules[shift.id] = []
        shiftrules = ShiftRule.objects.filter(shift=shift)
        for shiftrule in shiftrules:
            shiftruleroles = shiftrule.shiftrulerole_set.all()
            role_count = {}
            for shiftrulerole in shiftruleroles:
                role_count[shiftrulerole.role.id] = shiftrulerole.count
            shift_rules[shift.id].append(role_count)

    # Intermediate shift rule variables
    intermediate_vars = {
        (shift_id, rule_num): model.NewBoolVar(f"s{shift_id}r{rule_num}")
        for shift_id in shift_rules
        for rule_num, rule in enumerate(shift_rules[shift_id])
    }

    # Only one shift rule at a time can be satisfied
    for shift_id in shift_rules:
        if len(shift_rules[shift_id]) >= 1:
            model.Add(
                sum(
                    intermediate_vars[(shift_id, rule_num)]
                    for rule_num, rule in enumerate(shift_rules[shift_id])
                )
                == 1
            )

    # Enforce one shift rule per shift per timeslot
    for shift_id in shift_rules:
        if len(shift_rules[shift_id]) >= 1:
            for rule_num, rule in enumerate(shift_rules[shift_id]):
                for role_id in rule:
                    role_count = rule[role_id]
                    for timeslot in timeslots.filter(shift__id=shift_id):
                        # print(timeslot.date, shift_id, role_id, role_count)
                        model.Add(
                            sum(
                                shift_vars[
                                    (
                                        nurse.id,
                                        role_id,
                                        timeslot.date,
                                        timeslot.id,
                                    )
                                ]
                                for nurse in nurses.filter(roles__id=role_id)
                            )
                            == role_count
                        ).OnlyEnforceIf(
                            intermediate_vars[(shift_id, rule_num)]
                        )

    # Assign at most one shift per day per nurse
    for nurse in nurses:
        for date in dates:
            model.Add(
                sum(
                    shift_vars[(nurse.id, role.id, date, timeslot.id)]
                    for role in nurse.roles.all()
                    for timeslot in TimeSlot.objects.filter(
                        date=date
                    ).order_by("shift__shift_type")
                )
                <= 1
            )

    # Enforce shifts per roster for each nurse
    for nurse in nurses:
        num_shifts_worked = sum(
            shift_vars[(nurse.id, role.id, date, timeslot.id)]
            for role in nurse.roles.all()
            for date in dates
            for timeslot in TimeSlot.objects.filter(date=date).order_by(
                "shift__shift_type"
            )
        )
        if nurse.shifts_per_roster != 0:
            model.Add(nurse.shifts_per_roster == num_shifts_worked)

    # Maximise the number of satisfied shift requests
    model.Maximize(
        sum(
            shift_requests[n][d][s]
            * shift_vars[(nurse.id, role.id, date, timeslot.id)]
            for n, nurse in enumerate(nurses)
            for role in nurse.roles.all()
            for d, date in enumerate(dates)
            for s, timeslot in enumerate(
                TimeSlot.objects.filter(date=date).order_by(
                    "shift__shift_type"
                )
            )
        )
    )

    # Create the solver and solve
    solver = cp_model.CpSolver()
    solver.Solve(model)
    for value in intermediate_vars.values():
        print(value, solver.Value(value))

    for d, date in enumerate(dates):
        # print("Day", d)
        for n, nurse in enumerate(nurses):
            for role in nurse.roles.all():
                for s, timeslot in enumerate(
                    TimeSlot.objects.filter(date=date).order_by(
                        "shift__shift_type"
                    )
                ):
                    if (
                        solver.Value(
                            shift_vars[(nurse.id, role.id, date, timeslot.id)]
                        )
                        == 1
                    ):
                        if shift_requests[n][d][s] >= 1:
                            # print("Nurse", n, "works shift", s, "(requested).")
                            TimeSlot.objects.get(
                                date=date, shift=timeslot.shift
                            ).staff.add(nurse)
                        else:
                            # print(
                            #     "Nurse",
                            #     n,
                            #     "works shift",
                            #     s,
                            #     "(not requested).",
                            # )
                            TimeSlot.objects.get(
                                date=date, shift=timeslot.shift
                            ).staff.add(nurse)
        # print()

    # Statistics.
    # print()
    # print("Statistics")
    # print(
    #     "  - Number of shift requests met = %i" % solver.ObjectiveValue(),
    #     "(out of",
    #     num_nurses * min_shifts_per_nurse,
    #     ")",
    # )
    # print("  - wall time       : %f s" % solver.WallTime())

    return HttpResponseRedirect(reverse("timeslot_list"))


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
