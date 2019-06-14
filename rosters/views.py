import datetime
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

# from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from ortools.sat.python import cp_model
from django.contrib.auth import get_user_model
from django.contrib import messages
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


class SolutionNotFeasible(Exception):
    pass


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
    success_url = reverse_lazy("timeslot_list")

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        start_date = form.cleaned_data["start_date"]
        num_days = form.cleaned_data["num_days"]
        try:
            self.generate_roster(start_date, num_days)
        except SolutionNotFeasible:
            messages.error(
                self.request,
                (
                    "Could not generate roster,"
                    " try changing rules or staff availability."
                ),
            )
        return super().form_valid(form)

    def generate_roster(self, start_date, num_days):

        nurses = get_user_model().objects.all()
        shifts = Shift.objects.all().order_by("shift_type")

        # Delete existing shifts in date range
        date_range = [
            start_date.date(),
            start_date.date() + datetime.timedelta(days=num_days),
        ]
        TimeSlot.objects.filter(date__range=date_range).delete()

        leaves = Leave.objects.filter(date__range=date_range)

        # Create dates and timeslots
        dates = []
        date = start_date.date()
        for day in range(num_days):
            dates.append(date)
            day_of_week = date.weekday()
            for shift in shifts:
                if (
                    (shift.monday and day_of_week == 0)
                    or (shift.tuesday and day_of_week == 1)
                    or (shift.wednesday and day_of_week == 2)
                    or (shift.thursday and day_of_week == 3)
                    or (shift.friday and day_of_week == 4)
                    or (shift.saturday and day_of_week == 5)
                    or (shift.sunday and day_of_week == 6)
                ):
                    TimeSlot.objects.create(date=date, shift=shift)
            date += datetime.timedelta(days=1)
        timeslots = TimeSlot.objects.filter(date__range=date_range)

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
                    for timeslot in TimeSlot.objects.filter(
                        date=date
                    ).order_by("shift__shift_type"):
                        n = nurse.id
                        r = role.id
                        d = date
                        t = timeslot.id
                        shift_vars[(n, r, d, t)] = model.NewBoolVar(
                            f"shift_n{n}r{r}d{d}t{t}"
                        )

        # Create shift variables and fixed constraints
        # for previous roster period
        date_range = [
            start_date.date() - datetime.timedelta(days=num_days),
            start_date.date() - datetime.timedelta(days=1),
        ]
        previous_timeslots = TimeSlot.objects.filter(date__range=date_range)
        for timeslot in previous_timeslots:
            for nurse in timeslot.staff.all():
                n = nurse.id
                r = nurse.roles.all()[0]
                d = timeslot.date
                t = timeslot.id
                shift_vars[(n, r, d, t)] = model.NewBoolVar(
                    f"shift_n{n}r{r}d{d}t{t}"
                )
                model.Add(shift_vars[(n, r, d, t)] == 1)

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

        # Exclude leave dates from roster
        for timeslot in timeslots:
            for leave in leaves:
                if timeslot.date == leave.date:
                    for role in leave.staff_member.roles.all():
                        model.Add(
                            shift_vars[
                                (
                                    leave.staff_member.id,
                                    role.id,
                                    timeslot.date,
                                    timeslot.id,
                                )
                            ]
                            == 0
                        )

        # Enforce shift sequences / staff rules
        # Need to look at previous roster period also
        extended_dates = []
        date = start_date.date() - datetime.timedelta(days=num_days)
        for day in range(2 * num_days):
            extended_dates.append(date)
            date += datetime.timedelta(days=1)
        for nurse in nurses:
            for staff_rule in nurse.staffrule_set.all():
                invalid_shift_sequence = OrderedDict()
                staff_rule_shifts = staff_rule.staffruleshift_set.all().order_by(
                    "position"
                )
                for staff_rule_shift in staff_rule_shifts:
                    invalid_shift_sequence.setdefault(
                        staff_rule_shift.position, []
                    ).append(staff_rule_shift.shift)
                    # invalid_shift_sequence.append(staff_rule_shift.shift)
                sequence_size = len(invalid_shift_sequence)
                # print(invalid_shift_sequence)
                shift_vars_in_seq = []
                for date in extended_dates:
                    shift_vars_in_seq = []
                    for day_num in invalid_shift_sequence:
                        # for day_num, invalid_shift in enumerate(
                        #     invalid_shift_sequence
                        # ):
                        for invalid_shift in invalid_shift_sequence[day_num]:
                            try:
                                day_to_test = date + datetime.timedelta(
                                    days=day_num
                                )
                                timeslot_to_check = TimeSlot.objects.get(
                                    date=day_to_test, shift=invalid_shift
                                )
                            except TimeSlot.DoesNotExist:
                                break
                            for role in nurse.roles.all():
                                try:
                                    shift_vars_in_seq.append(
                                        shift_vars[
                                            (
                                                nurse.id,
                                                role.id,
                                                day_to_test,
                                                timeslot_to_check.id,
                                            )
                                        ]
                                    )
                                except KeyError:
                                    continue
                        # print(
                        #     "Shift vars in seq:",
                        #     invalid_shift_sequence,
                        #     shift_vars_in_seq,
                        # )
                    model.Add(sum(shift_vars_in_seq) < sequence_size)

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
                                    for nurse in nurses.filter(
                                        roles__id=role_id
                                    )
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
        solver.parameters.max_time_in_seconds = 60
        solution_status = solver.Solve(model)
        if (
            solution_status != cp_model.FEASIBLE
            and solution_status != cp_model.OPTIMAL
        ):
            raise SolutionNotFeasible("No feasible solutions.")

        # for value in intermediate_vars.values():
        #     print(value, solver.Value(value))

        for d, date in enumerate(dates):
            print(f"Day {d}:")
            for n, nurse in enumerate(nurses):
                for role in nurse.roles.all():
                    for s, timeslot in enumerate(
                        TimeSlot.objects.filter(date=date).order_by(
                            "shift__shift_type"
                        )
                    ):
                        if (
                            solver.Value(
                                shift_vars[
                                    (nurse.id, role.id, date, timeslot.id)
                                ]
                            )
                            == 1
                        ):
                            if shift_requests[n][d][s] >= 1:
                                print(
                                    f"*** Request Successful *** "
                                    f"{nurse.last_name}, {nurse.first_name}"
                                    f" requested shift"
                                    f" {timeslot.shift.shift_type}"
                                    f" and was assigned."
                                )
                                TimeSlot.objects.get(
                                    date=date, shift=timeslot.shift
                                ).staff.add(nurse)
                            else:
                                print(
                                    f"{nurse.last_name}, {nurse.first_name}"
                                    f" did not request shift"
                                    f" {timeslot.shift.shift_type}"
                                    f" and was assigned."
                                )
                                TimeSlot.objects.get(
                                    date=date, shift=timeslot.shift
                                ).staff.add(nurse)
                        else:
                            if shift_requests[n][d][s] >= 1:
                                print(
                                    f"*** Request Failed *** "
                                    f"{nurse.last_name}, {nurse.first_name}"
                                    f" requested shift"
                                    f" {timeslot.shift.shift_type}"
                                    f" but was not assigned."
                                )
            print()


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
