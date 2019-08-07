"""Business logic."""

import datetime
import logging
from collections import OrderedDict

from ortools.sat.python import cp_model
from django.contrib.auth import get_user_model

from .models import Leave, Role, Shift, ShiftRule, TimeSlot, Day


log = logging.getLogger("django")


class SolutionNotFeasible(Exception):
    """Exception for when there is no feasible solution."""

    pass


class TooManyStaff(Exception):
    """Exception for when there are too many staff."""

    pass


class RosterGenerator:
    """Roster generator."""

    def __init__(self, start_date):
        """Create starting conditions."""
        self.nurses = get_user_model().objects.filter(available=True)
        self.shifts = Shift.objects.all().order_by("shift_type")
        self.num_days = Day.objects.count()
        self.date_range = [
            start_date.date(),
            start_date.date() + datetime.timedelta(days=self.num_days),
        ]
        self.previous_date_range = [
            start_date.date() - datetime.timedelta(days=self.num_days),
            start_date.date() - datetime.timedelta(days=1),
        ]
        self.leaves = Leave.objects.filter(date__range=self.date_range)
        self.dates = [
            (start_date + datetime.timedelta(days=n)).date()
            for n in range(self.num_days)
        ]
        self.extended_dates = [
            (
                start_date
                - datetime.timedelta(days=self.num_days)
                + datetime.timedelta(days=n)
            ).date()
            for n in range(2 * self.num_days)
        ]
        self.model = cp_model.CpModel()

    def _clear_existing_timeslots(self):
        # Delete existing timeslots in date range
        TimeSlot.objects.filter(date__range=self.date_range).delete()

    def _create_timeslots(self):
        # Create timeslots
        for day, date in enumerate(self.dates):
            for shift in self.shifts:
                day_group_days = shift.day_group.daygroupday_set.all()
                for day_group_day in day_group_days:
                    if day_group_day.day.number == day + 1:
                        TimeSlot.objects.create(date=date, shift=shift)
        self.timeslots = TimeSlot.objects.filter(date__range=self.date_range)

    def _check_if_too_many_staff(self):
        # Check if too many staff
        log.info("Too many staff check started...")
        total_staff_shifts = 0
        for nurse in self.nurses:
            leave_days = self.leaves.filter(
                staff_member=nurse, date__range=self.date_range
            ).count()
            if leave_days > nurse.shifts_per_roster:
                total_staff_shifts += 0
            else:
                total_staff_shifts += nurse.shifts_per_roster - leave_days
        total_shifts = 0
        for timeslot in self.timeslots:
            total_shifts += timeslot.shift.max_staff
        log.info("Total staff shifts: " + str(total_staff_shifts))
        log.info("Total shifts: " + str(total_shifts))
        if total_staff_shifts > total_shifts:
            log.info("Error: there are too many staff...")
            raise TooManyStaff("Too many staff.")
        log.info("Too many staff check completed...")

    def _collect_shift_requests(self):
        # Collect shift requests into friendly data structure
        log.info("Shift request collection started...")
        self.shift_requests = []
        for nurse in self.nurses:
            nurse_shift_requests = []
            preferences = nurse.preference_set.all()
            for date in self.dates:
                nurse_shift_requests_for_day = []
                for timeslot in TimeSlot.objects.filter(date=date).order_by(
                    "shift__shift_type"
                ):
                    priority = 0
                    for preference in preferences:
                        if (
                            preference.date == date
                            and preference.shift == timeslot.shift
                        ):
                            if preference.like:
                                priority = preference.priority
                            else:
                                priority = -preference.priority
                    nurse_shift_requests_for_day.append(priority)
                nurse_shift_requests.append(nurse_shift_requests_for_day)
            self.shift_requests.append(nurse_shift_requests)
        log.info("Shift request collection completed...")
        log.debug(self.shift_requests)

    def _create_shift_vars(self):
        """Create shift variables.

        shift_vars[(n, r, d, t)]:
        nurse 'n' with role 'r' works on date 'd' in timeslot 't'
        """
        log.info("Shift variable creation started...")
        self.shift_vars = {}
        for nurse in self.nurses:
            for role in nurse.roles.all():
                for date in self.dates:
                    for timeslot in self.timeslots.filter(date=date).order_by(
                        "shift__shift_type"
                    ):
                        n = nurse.id
                        r = role.id
                        d = date
                        t = timeslot.id
                        self.shift_vars[(n, r, d, t)] = self.model.NewBoolVar(
                            f"shift_n{n}r{r}d{d}t{t}"
                        )
        log.info("Shift variable creation completed...")
        log.debug(self.shift_vars.keys())

    def _create_previous_shift_vars(self):
        # Create shift variables and fixed constraints
        # for previous roster period
        log.info("Creation of shift variables for previous period started...")
        previous_timeslots = TimeSlot.objects.filter(
            date__range=self.previous_date_range
        )
        for timeslot in previous_timeslots:
            for nurse in timeslot.staff.all():
                n = nurse.id
                r = nurse.roles.all()[0]
                d = timeslot.date
                t = timeslot.id
                self.shift_vars[(n, r, d, t)] = self.model.NewBoolVar(
                    f"shift_n{n}r{r}d{d}t{t}"
                )
                self.model.Add(self.shift_vars[(n, r, d, t)] == 1)
        log.info(
            "Creation of shift variables for previous period completed..."
        )

    def _exclude_leave_dates(self):
        # Exclude leave dates from roster
        log.info("Exclusion of leave dates started...")
        for timeslot in self.timeslots:
            for leave in self.leaves:
                if timeslot.date == leave.date:
                    for role in leave.staff_member.roles.all():
                        self.model.Add(
                            self.shift_vars[
                                (
                                    leave.staff_member.id,
                                    role.id,
                                    timeslot.date,
                                    timeslot.id,
                                )
                            ]
                            == 0
                        )
        log.info("Exclusion of leave dates completed...")

    def _enforce_shift_sequences(self):
        """Enforce shift sequences / staff rules.

        Need to look at previous roster period also
        """
        log.info("Addition of shift sequence rules started...")
        timeslot_ids = {}
        for date in self.extended_dates:
            timeslot_ids[date] = {}
            for shift in self.shifts:
                try:
                    timeslot_ids[date][shift] = TimeSlot.objects.get(
                        date=date, shift=shift
                    ).id
                except TimeSlot.DoesNotExist:
                    continue
        for nurse in self.nurses:
            roles = nurse.roles.all()
            for staff_rule in nurse.staffrule_set.all():
                invalid_shift_sequence = OrderedDict()
                staff_rule_shifts = staff_rule.staffruleshift_set.all()
                staff_rule_shifts = staff_rule_shifts.order_by("position")
                for staff_rule_shift in staff_rule_shifts:
                    invalid_shift_sequence.setdefault(
                        staff_rule_shift.position, []
                    ).append(staff_rule_shift.shift)
                sequence_size = len(invalid_shift_sequence)
                day_group_day_set = staff_rule.day_group.daygroupday_set.all()
                sequence_days = [
                    day_group_day.day.number
                    for day_group_day in day_group_day_set
                ]
                shift_vars_in_seq = []
                for date in self.extended_dates:
                    shift_vars_in_seq = []
                    shift_vars_blank = []
                    last_day_in_sequence = list(invalid_shift_sequence.keys())[
                        -1
                    ]
                    all_days = [
                        day for day in range(1, last_day_in_sequence + 1)
                    ]
                    for day_num in all_days:
                        if day_num not in invalid_shift_sequence.keys():
                            day_to_test = date + datetime.timedelta(
                                days=day_num - 1
                            )
                            for role in roles:
                                try:
                                    for timeslot in self.timeslots.filter(
                                        date=day_to_test
                                    ):
                                        shift_vars_blank.append(
                                            self.shift_vars[
                                                (
                                                    nurse.id,
                                                    role.id,
                                                    day_to_test,
                                                    timeslot.id,
                                                )
                                            ]
                                        )
                                except KeyError:
                                    continue
                    for day_num in invalid_shift_sequence:
                        for invalid_shift in invalid_shift_sequence[day_num]:
                            day_to_test = date + datetime.timedelta(
                                days=day_num - 1
                            )

                            # Skip if day not in day group for sequence
                            delta = (day_to_test - self.dates[0]).days
                            if delta < 0:
                                day_group_day_num = delta + self.num_days + 1
                            else:
                                day_group_day_num = delta + 1
                            if day_group_day_num not in sequence_days:
                                break

                            for role in roles:
                                try:
                                    shift_vars_in_seq.append(
                                        self.shift_vars[
                                            (
                                                nurse.id,
                                                role.id,
                                                day_to_test,
                                                timeslot_ids[day_to_test][
                                                    invalid_shift
                                                ],
                                            )
                                        ]
                                    )
                                except KeyError:
                                    continue
                    if len(shift_vars_blank) == 0:
                        self.model.Add(sum(shift_vars_in_seq) < sequence_size)
                    else:
                        for item, var in enumerate(shift_vars_blank):
                            shift_vars_blank[item] = var.Not()
                        self.model.Add(
                            sum(shift_vars_in_seq) < sequence_size
                        ).OnlyEnforceIf(shift_vars_blank)
        log.info("Addition of shift sequence rules completed...")

    def _collect_skill_mix_rules(self):
        """Collect shift rules into friendly structure."""
        log.info("Collection of skill mix rules started...")
        self.shift_rules = {}
        for shift in self.shifts:
            self.shift_rules[shift.id] = []
            shiftrules = ShiftRule.objects.filter(shift=shift)
            for shiftrule in shiftrules:
                shiftruleroles = shiftrule.shiftrulerole_set.all()
                role_count = {}
                for role in Role.objects.all():
                    role_count[role.id] = 0
                for shiftrulerole in shiftruleroles:
                    role_count[shiftrulerole.role.id] = shiftrulerole.count
                self.shift_rules[shift.id].append(role_count)
        log.info("Collection of skill mix rules completed...")
        log.debug(self.shift_rules)

    def _create_intermediate_skill_mix_vars(self):
        # Intermediate shift rule variables
        log.info("Creation of skill mix intermediate variables started...")
        self.intermediate_skill_mix_vars = {
            (timeslot.id, rule_num): self.model.NewBoolVar(
                f"t{timeslot.id}r{rule_num}"
            )
            for timeslot in self.timeslots
            for rule_num, rule in enumerate(
                self.shift_rules[timeslot.shift.id]
            )
        }
        log.info("Creation of skill mix intermediate variables completed...")
        log.debug(self.intermediate_skill_mix_vars)

    def _enforce_one_skill_mix_rule_at_a_time(self):
        """Only one skill mix rule at a time should be enforced."""
        log.info("Enforcement of one shift rule at a time started...")
        for timeslot in self.timeslots:
            if len(self.shift_rules[timeslot.shift.id]) >= 1:
                self.model.Add(
                    sum(
                        self.intermediate_skill_mix_vars[
                            (timeslot.id, rule_num)
                        ]
                        for rule_num, rule in enumerate(
                            self.shift_rules[timeslot.shift.id]
                        )
                    )
                    == 1
                )
        log.info("Enforcement of one shift rule at a time completed...")

    def _enforce_skill_mix_rules(self):
        """Enforce one skill mix rule per shift per timeslot."""
        log.info("Enforcement of skill mix rules started...")
        for shift_id in self.shift_rules:
            if len(self.shift_rules[shift_id]) >= 1:
                for rule_num, rule in enumerate(self.shift_rules[shift_id]):
                    for role_id in rule:
                        role_count = rule[role_id]
                        for timeslot in self.timeslots.filter(
                            shift__id=shift_id
                        ):
                            self.model.Add(
                                sum(
                                    self.shift_vars[
                                        (
                                            nurse.id,
                                            role_id,
                                            timeslot.date,
                                            timeslot.id,
                                        )
                                    ]
                                    for nurse in self.nurses.filter(
                                        roles__id=role_id
                                    )
                                )
                                == role_count
                            ).OnlyEnforceIf(
                                self.intermediate_skill_mix_vars[
                                    (timeslot.id, rule_num)
                                ]
                            )
        log.info("Enforcement of skill mix rules completed...")

    def _enforce_one_shift_per_day(self):
        """Assign at most one shift per day per nurse."""
        log.info("Restriction of staff to one shift per day started...")
        for nurse in self.nurses:
            for date in self.dates:
                if nurse.shifts_per_roster != 0:  # Zero means unlimited shifts
                    self.model.Add(
                        sum(
                            self.shift_vars[
                                (nurse.id, role.id, date, timeslot.id)
                            ]
                            for role in nurse.roles.all()
                            for timeslot in TimeSlot.objects.filter(
                                date=date
                            ).order_by("shift__shift_type")
                        )
                        <= 1
                    )
        log.info("Restriction of staff to one shift per day completed...")

    def _enforce_shifts_per_roster(self):
        """Enforce shifts per roster for each nurse."""
        log.info("Enforcement of shifts per roster started...")
        for nurse in self.nurses:
            num_shifts_worked = sum(
                self.shift_vars[(nurse.id, role.id, date, timeslot.id)]
                for role in nurse.roles.all()
                for date in self.dates
                for timeslot in TimeSlot.objects.filter(date=date).order_by(
                    "shift__shift_type"
                )
            )
            if nurse.shifts_per_roster != 0:  # Zero means unlimited shifts
                leave_days = Leave.objects.filter(
                    staff_member=nurse, date__range=self.date_range
                ).count()
                shifts_per_roster = nurse.shifts_per_roster - leave_days
                if shifts_per_roster < 0:
                    shifts_per_roster = 0
                self.model.Add(shifts_per_roster == num_shifts_worked)
        log.info("Enforcement of shifts per roster completed...")

    def _maximise_staff_requests(self):
        """Maximise the number of satisfied staff requests."""
        log.info("Maximising of staff requests started...")
        self.model.Maximize(
            sum(
                self.shift_requests[n][d][s]
                * self.shift_vars[(nurse.id, role.id, date, timeslot.id)]
                for n, nurse in enumerate(self.nurses)
                for role in nurse.roles.all()
                for d, date in enumerate(self.dates)
                for s, timeslot in enumerate(
                    TimeSlot.objects.filter(date=date).order_by(
                        "shift__shift_type"
                    )
                )
            )
        )
        log.info("Maximising of staff requests completed...")

    def _solve_roster(self):
        """Create the solver and solve."""
        self.solver = cp_model.CpSolver()
        self.solver.parameters.max_time_in_seconds = 120
        log.info("Solver started...")
        solution_status = self.solver.Solve(self.model)
        log.info("Solver finished...")
        if solution_status == cp_model.INFEASIBLE:
            log.info("Solution is INFEASIBLE")
        if solution_status == cp_model.MODEL_INVALID:
            log.info("Solution is MODEL_INVALID")
        if solution_status == cp_model.UNKNOWN:
            log.info("Solution is UNKNOWN")
        if (
            solution_status != cp_model.FEASIBLE
            and solution_status != cp_model.OPTIMAL
        ):
            log.info("No feasible solution, raising exception...")
            raise SolutionNotFeasible("No feasible solutions.")

    def _populate_roster(self):
        """Poulate roster."""
        log.info("Population of roster started...")
        for d, date in enumerate(self.dates):
            for n, nurse in enumerate(self.nurses):
                for role in nurse.roles.all():
                    for s, timeslot in enumerate(
                        TimeSlot.objects.filter(date=date).order_by(
                            "shift__shift_type"
                        )
                    ):
                        if (
                            self.solver.Value(
                                self.shift_vars[
                                    (nurse.id, role.id, date, timeslot.id)
                                ]
                            )
                            == 1
                        ):
                            TimeSlot.objects.get(
                                date=date, shift=timeslot.shift
                            ).staff.add(nurse)
                            if self.shift_requests[n][d][s] > 0:
                                log.info(
                                    f"Request Successful: "
                                    f"{nurse.last_name}, {nurse.first_name}"
                                    f" {role.role_name}"
                                    f" requested shift"
                                    f" {timeslot.shift.shift_type}"
                                    f" on"
                                    f" {timeslot.date}"
                                    f" and was assigned."
                                )
                            elif self.shift_requests[n][d][s] < 0:
                                log.info(
                                    f"Request Failed: "
                                    f"{nurse.last_name}, {nurse.first_name}"
                                    f" {role.role_name}"
                                    f" requested not to work shift"
                                    f" {timeslot.shift.shift_type}"
                                    f" on"
                                    f" {timeslot.date}"
                                    f" but was assigned."
                                )
                        else:
                            if self.shift_requests[n][d][s] > 0:
                                log.info(
                                    f"Request Failed: "
                                    f"{nurse.last_name}, {nurse.first_name}"
                                    f" {role.role_name}"
                                    f" requested shift"
                                    f" {timeslot.shift.shift_type}"
                                    f" on"
                                    f" {timeslot.date}"
                                    f" but was not assigned."
                                )
                            elif self.shift_requests[n][d][s] < 0:
                                log.info(
                                    f"Request Succeeded: "
                                    f"{nurse.last_name}, {nurse.first_name}"
                                    f" {role.role_name}"
                                    f" requested not to work shift"
                                    f" {timeslot.shift.shift_type}"
                                    f" on"
                                    f" {timeslot.date}"
                                    f" and was not assigned."
                                )
        log.info("Population of roster completed...")

    def create(self):
        """Create roster as per constraints."""
        self._clear_existing_timeslots()
        self._create_timeslots()
        self._check_if_too_many_staff()
        self._collect_shift_requests()
        self._create_shift_vars()
        self._create_previous_shift_vars()
        self._exclude_leave_dates()
        self._enforce_shift_sequences()
        self._collect_skill_mix_rules()
        self._create_intermediate_skill_mix_vars()
        self._enforce_one_skill_mix_rule_at_a_time()
        self._enforce_skill_mix_rules()
        self._enforce_one_shift_per_day()
        self._enforce_shifts_per_roster()
        self._maximise_staff_requests()
        self._solve_roster()
        self._populate_roster()


def get_roster_by_staff(start_date):
    """Create data structures for roster grouped by staff."""
    dates = []
    roster = OrderedDict()
    nurses = (
        get_user_model()
        .objects.all()
        .order_by("roles__role_name", "last_name", "first_name")
    )
    num_days = Day.objects.count()
    for nurse in nurses:
        roster[nurse.last_name + ", " + nurse.first_name] = OrderedDict()
        staff_roles = ""
        for role in nurse.roles.all().order_by("role_name"):
            staff_roles += role.role_name + " "
        roster[nurse.last_name + ", " + nurse.first_name][
            "roles"
        ] = staff_roles
        roster[nurse.last_name + ", " + nurse.first_name][
            "shifts_per_roster"
        ] = nurse.shifts_per_roster
        leaves = Leave.objects.filter(staff_member=nurse)
        dates = []
        for day in range(num_days):
            date = start_date + datetime.timedelta(days=day)
            date = date.date()
            dates.append(date)
            try:
                roster[nurse.last_name + ", " + nurse.first_name][
                    date
                ] = TimeSlot.objects.get(
                    date=date, staff=nurse.id
                ).shift.shift_type
            except TimeSlot.DoesNotExist:
                leave = leaves.filter(date=date).count()
                if leave == 0:
                    roster[nurse.last_name + ", " + nurse.first_name][
                        date
                    ] = "X"
                else:
                    roster[nurse.last_name + ", " + nurse.first_name][
                        date
                    ] = leaves.get(date=date).description
            except TimeSlot.MultipleObjectsReturned:
                timeslots = TimeSlot.objects.filter(date=date, staff=nurse.id)
                roster[nurse.last_name + ", " + nurse.first_name][date] = ""
                for timeslot in timeslots:
                    roster[nurse.last_name + ", " + nurse.first_name][
                        date
                    ] += (timeslot.shift.shift_type + " ")
    return dates, roster
