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
    num_nurses = nurses.count()
    shifts = Shift.objects.all()
    num_shifts = shifts.count()
    num_days = 14
    TimeSlot.objects.all().delete()
    date = datetime.date.today()
    for day in range(num_days):
        for shift in shifts:
            TimeSlot.objects.create(date=date, shift=shift)
        date += datetime.timedelta(days=1)
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
    # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'
    shift_vars = {}
    for n in range(num_nurses):
        for d in range(num_days):
            for s in range(num_shifts):
                shift_vars[(n, d, s)] = model.NewBoolVar(f"shift_n{n}d{d}s{s}")

    # Assign each shift to exactly 5 nurses
    for d in range(num_days):
        for s in range(num_shifts):
            model.Add(
                sum(shift_vars[(n, d, s)] for n in range(num_nurses)) == 5
            )

    # for s, shift in enumerate(shifts):
    #     shiftrules = shift.shiftrule_set.all()
    #     for shiftrule in shiftrules:
    #         shiftruleroles = shiftrulerole_set.all()
    #         for shiftrulerole in shiftruleroles:
    #             shiftrulerole.role
    #             shiftrulerole.count

    # rn_nurses = nurses.filter(roles__role_name="RN")
    # srn_nurses = nurses.filter(roles__role_name="SRN")

    # Map nurse pk to shift_vars n ?

    rn_nurses = []
    srn_nurses = []
    for n, nurse in enumerate(nurses):
        rn = False
        srn = False
        for role in nurse.roles.all():
            if role.role_name == "RN":
                rn = True
            if role.role_name == "SRN":
                srn = True
        if rn:
            rn_nurses.append(True)
        else:
            rn_nurses.append(False)
        if srn:
            srn_nurses.append(True)
        else:
            srn_nurses.append(False)

    print(rn_nurses, srn_nurses)

    for s, shift in enumerate(shifts):
        for d in range(num_days):
            model.Add(
                (
                    (
                        sum(
                            shift_vars[(n, d, s)]
                            for n, nurse in enumerate(nurses)
                            if rn_nurses[n]
                        )
                        >= 3
                        and sum(
                            shift_vars[(n, d, s)]
                            for n, nurse in enumerate(nurses)
                            if srn_nurses[n]
                        )
                        >= 1
                    )
                    # or (
                    #     sum(
                    #         shift_vars[(n, d, s)]
                    #         for n, nurse in enumerate(nurses)
                    #         if rn_nurses[n]
                    #     )
                    #     == 2
                    #     and sum(
                    #         shift_vars[(n, d, s)]
                    #         for n, nurse in enumerate(nurses)
                    #         if srn_nurses[n]
                    #     )
                    #     == 3
                    # )
                )
            )

    # Assign at most one shift per day per nurse
    for n, nurse in enumerate(nurses):
        for d in range(num_days):
            model.Add(
                sum(shift_vars[(n, d, s)] for s in range(num_shifts)) <= 1
            )

    # Enforce shifts per roster for each nurse
    for n, nurse in enumerate(nurses):
        num_shifts_worked = sum(
            shift_vars[(n, d, s)]
            for d in range(num_days)
            for s in range(num_shifts)
        )
        if nurse.shifts_per_roster != 0:  # 0 means no limit / temporary staff
            model.Add(nurse.shifts_per_roster == num_shifts_worked)

    # Maximise the number of satisfied shift requests
    model.Maximize(
        sum(
            shift_requests[n][d][s] * shift_vars[(n, d, s)]
            for n in range(num_nurses)
            for d in range(num_days)
            for s in range(num_shifts)
        )
    )

    # Create the solver and solve
    solver = cp_model.CpSolver()
    solver.Solve(model)
    date = datetime.date.today()
    for d in range(num_days):
        print("Day", d)
        for n, nurse in enumerate(nurses):
            for s, shift in enumerate(shifts):
                if solver.Value(shift_vars[(n, d, s)]) == 1:
                    if shift_requests[n][d][s] >= 1:
                        print("Nurse", n, "works shift", s, "(requested).")
                        TimeSlot.objects.get(date=date, shift=shift).staff.add(
                            nurse
                        )
                    else:
                        print("Nurse", n, "works shift", s, "(not requested).")
                        TimeSlot.objects.get(date=date, shift=shift).staff.add(
                            nurse
                        )
        print()
        date += datetime.timedelta(days=1)

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
