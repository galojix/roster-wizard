"""Business logic."""

import datetime
import logging
import math
from collections import OrderedDict

from ortools.sat.python import cp_model
from django.contrib.auth import get_user_model

# from django.db import connection, reset_queries

from .models import Leave, Role, Shift, ShiftRule, TimeSlot, Day, StaffRequest


log = logging.getLogger(__name__)


class SolutionNotFeasible(Exception):
    """Exception for when there is no feasible solution."""

    pass


class RosterGenerator:
    """Roster generator."""

    def __init__(self, start_date):
        """Create starting conditions."""
        self.workers = get_user_model().objects.filter(available=True)
        self.worker_lookup = {
            worker.id: worker_num for worker_num, worker in enumerate(self.workers)
        }
        self.shifts = Shift.objects.all().order_by("shift_type")
        self.shift_lookup = {
            shift.id: shift_num for shift_num, shift in enumerate(self.shifts)
        }
        self.num_days = Day.objects.count()
        self.date_range = [
            start_date.date(),
            start_date.date() + datetime.timedelta(days=self.num_days - 1),
        ]
        self.previous_date_range = [
            start_date.date() - datetime.timedelta(days=self.num_days),
            start_date.date() - datetime.timedelta(days=1),
        ]
        self.extended_date_range = [
            start_date.date() - datetime.timedelta(days=self.num_days),
            start_date.date() + datetime.timedelta(days=self.num_days - 1),
        ]
        self.leaves = Leave.objects.filter(date__range=self.date_range)
        self.staffrequests = StaffRequest.objects.filter(date__range=self.date_range)
        self.days = [day.number for day in Day.objects.order_by("number")]
        self.dates = [
            (start_date + datetime.timedelta(days=n)).date()
            for n in range(self.num_days)
        ]
        self.date_lookup = {date: day_num for day_num, date in enumerate(self.dates)}
        self.extended_dates = [
            (
                start_date
                - datetime.timedelta(days=self.num_days)
                + datetime.timedelta(days=n)
            ).date()
            for n in range(2 * self.num_days)
        ]
        self.model = cp_model.CpModel()
        self.complete = False

    def _clear_existing_timeslots(self):
        # Delete existing timeslots in date range
        TimeSlot.objects.filter(date__range=self.date_range).delete()

    def _create_timeslots(self):
        # Create timeslots
        for shift in self.shifts:
            daygroupdays = shift.daygroup.daygroupday_set.all()
            for daygroupday in daygroupdays:
                TimeSlot.objects.create(
                    date=self.dates[daygroupday.day.number - 1], shift=shift
                )
        self.timeslots = TimeSlot.objects.filter(date__range=self.date_range)

    def _create_timeslots_lookup(self):
        # Create timeslot id lookup
        self.timeslots_lookup = {}
        for date in self.extended_dates:
            timeslots_for_date = list(
                TimeSlot.objects.filter(date=date).order_by("shift__shift_type")
            )
            self.timeslots_lookup[date] = timeslots_for_date

    def _collect_shift_requests(self):
        """Collect shift requests into friendly data structure."""
        log.info("Shift request collection started...")
        self.shift_requests = [
            [[0 for _ in self.shifts] for _ in self.days] for worker in self.workers
        ]
        for staffrequest in self.staffrequests:
            worker_num = self.worker_lookup[staffrequest.staff_member.id]
            day_num = self.date_lookup[staffrequest.date]
            shift_num = self.shift_lookup[staffrequest.shift.id]
            self.shift_requests[worker_num][day_num][shift_num] = (
                staffrequest.priority if staffrequest.like else -staffrequest.priority
            )
        log.info("Shift request collection completed...")

    def _create_shift_vars(self):
        """Create shift variables.

        shift_vars[(n, r, d, t)]:
        worker 'n' with role 'r' works on date 'd' in timeslot 't'
        """
        log.info("Shift variable creation started...")
        self.shift_vars = {
            (worker.id, role.id, date, timeslot.id): self.model.NewBoolVar(
                f"shift_n{worker.id}r{role.id}d{date}t{timeslot.id}"
            )
            for date in self.dates
            for timeslot in self.timeslots_lookup[date]
            for worker in self.workers
            for role in worker.roles.all()
        }
        log.info("Shift variable creation completed...")

    def _create_previous_shift_vars(self):
        # Create shift variables and fixed constraints
        # for previous roster period
        log.info("Creation of shift variables for previous period started...")
        previous_timeslots = TimeSlot.objects.filter(
            date__range=self.previous_date_range
        )
        for timeslot in previous_timeslots:
            for worker in self.workers:
                n = worker.id
                r = worker.roles.all()[0].id
                d = timeslot.date
                t = timeslot.id
                self.shift_vars[(n, r, d, t)] = self.model.NewBoolVar(
                    f"shift_n{n}r{r}d{d}t{t}"
                )
                if worker in timeslot.staff.all():
                    self.model.Add(self.shift_vars[(n, r, d, t)] == 1)
                else:
                    self.model.Add(self.shift_vars[(n, r, d, t)] == 0)
        log.info("Creation of shift variables for previous period completed...")

    def _exclude_leave_dates(self):
        """Ensure staff members are not assigned to any shifts while on leave."""
        log.info("Exclusion of leave dates started...")
        for leave in self.leaves:
            for role in leave.staff_member.roles.all():
                for timeslot in self.timeslots_lookup[leave.date]:
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

    def _get_timeslot_ids(self):
        """Map date and shift to timeslot ID."""
        timeslots = TimeSlot.objects.filter(date__range=self.extended_date_range)
        return {(timeslot.date, timeslot.shift): timeslot.id for timeslot in timeslots}

    def _get_shift_seq(self, shiftsequence):
        """Create shift sequence for each rule.

        Example: { 1: [ "E", "L", "N"], 2: ["E", "L"] }
        """
        shift_sequence = OrderedDict()
        staffruleshifts = shiftsequence.staffruleshift_set.order_by("position")
        for staffruleshift in staffruleshifts:
            shift_sequence.setdefault(staffruleshift.position, []).append(
                staffruleshift.shift
            )
        return shift_sequence

    def _get_work_days_in_seq(self, shift_seq):
        """Get number of working days in shift sequence."""
        return sum(shift_seq[position][0] is not None for position in shift_seq)

    def _get_all_days_in_seq(self, shiftsequence):
        """Get number of days in staff rule."""
        daygroupday_set = shiftsequence.daygroup.daygroupday_set.all()
        return [daygroupday.day.number for daygroupday in daygroupday_set]

    def _get_non_working_shift_variables_in_sequence(
        self,
        date,
        shift_seq,
        all_days_in_seq,
        roles,
        worker,
    ):
        """Find non-working shift variables in shift sequence.

        A blank/None position (no shift) in a staff rule means no shift worked
        that day.

        """
        shift_vars_in_seq_off = {}
        for day_num in shift_seq:
            shift_vars_in_seq_off[day_num] = []
            for shift in shift_seq[day_num]:
                if shift is None:
                    day_to_test = date + datetime.timedelta(days=day_num - 1)

                    # Skip if day not in day group for sequence
                    delta = (day_to_test - self.dates[0]).days
                    daygroupday_num = (
                        delta + self.num_days + 1 if delta < 0 else delta + 1
                    )
                    if daygroupday_num not in all_days_in_seq:
                        break

                    for role in roles:
                        try:
                            for timeslot in self.timeslots_lookup[day_to_test]:
                                shift_vars_in_seq_off[day_num].append(
                                    self.shift_vars[
                                        (
                                            worker.id,
                                            role.id,
                                            day_to_test,
                                            timeslot.id,
                                        )
                                    ]
                                )
                        except KeyError:
                            continue
        return shift_vars_in_seq_off

    def _get_working_shift_variables_in_sequence(
        self,
        date,
        shift_seq,
        all_days_in_seq,
        roles,
        worker,
        timeslot_ids,
    ):
        """Find working day shift variables in shift sequence."""
        shift_vars_in_seq_on = {}
        for day_num in shift_seq:
            shift_vars_in_seq_on[day_num] = []
            for shift in shift_seq[day_num]:
                if shift is not None:
                    day_to_test = date + datetime.timedelta(days=day_num - 1)

                    # Skip if day not in day group for sequence
                    delta = (day_to_test - self.dates[0]).days
                    daygroupday_num = (
                        delta + self.num_days + 1 if delta < 0 else delta + 1
                    )
                    if daygroupday_num not in all_days_in_seq:
                        break

                    for role in roles:
                        try:
                            shift_vars_in_seq_on[day_num].append(
                                self.shift_vars[
                                    (
                                        worker.id,
                                        role.id,
                                        day_to_test,
                                        timeslot_ids[(day_to_test, shift)],
                                    )
                                ]
                            )
                        except KeyError:
                            continue
        return shift_vars_in_seq_on

    def _precompute_invalid_shift_sequences(self):
        self.invalid_shift_sequences = {}
        for worker in self.workers:
            for shiftsequence in worker.shiftsequence_set.all():
                invalid_shift_seq = self._get_shift_seq(shiftsequence)
                self.invalid_shift_sequences[(worker.id, shiftsequence.id)] = (
                    invalid_shift_seq
                )

    def _enforce_invalid_shift_sequences(self):
        """Enforce invalid shift sequences / staff rules.

        Need to look at previous roster period also
        """
        log.info("Enforcement of invalid shift sequence rules started...")

        timeslot_ids = self._get_timeslot_ids()

        for worker in self.workers:
            roles = worker.roles.all()
            for shiftsequence in worker.shiftsequence_set.all():
                invalid_shift_seq = self.invalid_shift_sequences[
                    (worker.id, shiftsequence.id)
                ]
                # invalid_shift_seq = self._get_shift_seq(shiftsequence)
                all_days_in_seq = self._get_all_days_in_seq(shiftsequence)

                for date in self.extended_dates:
                    shift_vars_in_seq_off = (
                        self._get_non_working_shift_variables_in_sequence(
                            date,
                            invalid_shift_seq,
                            all_days_in_seq,
                            roles,
                            worker,
                        )
                    )
                    shift_vars_in_seq_on = (
                        self._get_working_shift_variables_in_sequence(
                            date,
                            invalid_shift_seq,
                            all_days_in_seq,
                            roles,
                            worker,
                            timeslot_ids,
                        )
                    )

                    # Create intermediate vars
                    intermediate_vars = {
                        (
                            worker.id,
                            date,
                            shiftsequence.id,
                            position,
                        ): self.model.NewBoolVar(
                            f"w{worker.id}d{date}sr{shiftsequence.id}p{position}"
                        )
                        for position in shift_vars_in_seq_on
                    }

                    # Enforce "off" rule
                    for position in shift_vars_in_seq_off:
                        if len(shift_vars_in_seq_off[position]) > 0:
                            self.model.Add(
                                sum(shift_vars_in_seq_off[position]) >= 1
                            ).OnlyEnforceIf(
                                intermediate_vars[
                                    (worker.id, date, shiftsequence.id, position)
                                ]
                            )

                    # Enforce "on" rule
                    for position in shift_vars_in_seq_on:
                        if len(shift_vars_in_seq_on[position]) > 0:
                            self.model.Add(
                                sum(shift_vars_in_seq_on[position]) == 0
                            ).OnlyEnforceIf(
                                intermediate_vars[
                                    (worker.id, date, shiftsequence.id, position)
                                ]
                            )

                    # Enforce one intermediate variable to be true
                    # Only need to enforce one position per rule
                    all_intermediate_vars = [
                        value for item, value in intermediate_vars.items()
                    ]
                    self.model.Add(sum(all_intermediate_vars) >= 1)

        log.info("Enforcement of invalid shift sequence rules completed...")

    def _collect_skill_mix_rules(self):
        """Collect shift rules into friendly structure."""
        log.info("Collection of skill mix rules started...")
        self.shiftrules = {}
        for shift in self.shifts:
            self.shiftrules[shift.id] = []
            shiftrules = ShiftRule.objects.filter(shift=shift)
            for shiftrule in shiftrules:
                shiftruleroles = shiftrule.shiftrulerole_set.all()
                role_count = {role.id: 0 for role in Role.objects.all()}
                for shiftrulerole in shiftruleroles:
                    role_count[shiftrulerole.role.id] = shiftrulerole.count
                self.shiftrules[shift.id].append(role_count)
        log.info("Collection of skill mix rules completed...")

    def _create_intermediate_skill_mix_vars(self):
        # Intermediate shift rule variables
        log.info("Creation of skill mix intermediate variables started...")
        self.intermediate_skill_mix_vars = {
            (timeslot.id, rule_num): self.model.NewBoolVar(f"t{timeslot.id}r{rule_num}")
            for timeslot in self.timeslots
            for rule_num, rule in enumerate(self.shiftrules[timeslot.shift.id])
        }
        log.info("Creation of skill mix intermediate variables completed...")

    def _enforce_one_skill_mix_rule_at_a_time(self):
        """Only one skill mix rule at a time should be enforced."""
        log.info("Enforcement of one skill mix rule at a time started...")
        for timeslot in self.timeslots:
            if len(self.shiftrules[timeslot.shift.id]) >= 1:
                self.model.Add(
                    sum(
                        self.intermediate_skill_mix_vars[(timeslot.id, rule_num)]
                        for rule_num, rule in enumerate(
                            self.shiftrules[timeslot.shift.id]
                        )
                    )
                    == 1
                )
        log.info("Enforcement of one skill mix rule at a time completed...")

    def _enforce_skill_mix_rules(self):
        """Enforce one skill mix rule per shift per timeslot."""
        log.info("Enforcement of skill mix rules started...")
        for shift_id in self.shiftrules:
            shift_timeslots = self.timeslots.filter(shift__id=shift_id)
            if len(self.shiftrules[shift_id]) >= 1:
                for rule_num, rule in enumerate(self.shiftrules[shift_id]):
                    for role_id in rule:
                        workers = self.workers.filter(roles__id=role_id)
                        role_count = rule[role_id]
                        for timeslot in shift_timeslots:
                            self.model.Add(
                                sum(
                                    self.shift_vars[
                                        (
                                            worker.id,
                                            role_id,
                                            timeslot.date,
                                            timeslot.id,
                                        )
                                    ]
                                    for worker in workers
                                )
                                == role_count
                            ).OnlyEnforceIf(
                                self.intermediate_skill_mix_vars[
                                    (timeslot.id, rule_num)
                                ]
                            )
        log.info("Enforcement of skill mix rules completed...")

    def _enforce_one_shift_per_day(self):
        """Assign at most one shift per day per worker."""
        log.info("Restriction of staff to one shift per day started...")
        for date in self.dates:
            timeslots = TimeSlot.objects.filter(date=date)
            for worker in self.workers:
                roles = worker.roles.all()
                if worker.enforce_one_shift_per_day:
                    self.model.Add(
                        sum(
                            self.shift_vars[(worker.id, role.id, date, timeslot.id)]
                            for role in roles
                            for timeslot in timeslots
                        )
                        <= 1
                    )
        log.info("Restriction of staff to one shift per day completed...")

    def _get_shifts_per_roster(self, worker):
        """Get number of shifts to work in roster period."""
        leave_days = self.leaves.filter(staff_member=worker).count()
        work_fraction = 1 - (leave_days / self.num_days)
        shifts_per_roster = work_fraction * worker.shifts_per_roster
        if worker.max_shifts:
            shifts_per_roster = math.ceil(shifts_per_roster)
        else:
            shifts_per_roster = math.floor(shifts_per_roster)
        return shifts_per_roster

    def _enforce_shifts_per_roster(self):
        """Enforce shifts per roster for each worker."""
        log.info("Enforcement of shifts per roster started...")
        for worker in self.workers:
            num_shifts_worked = sum(
                self.shift_vars[(worker.id, role.id, date, timeslot.id)]
                for role in worker.roles.all()
                for date in self.dates
                for timeslot in self.timeslots_lookup[date]
            )
            if worker.enforce_shifts_per_roster:
                shifts_per_roster = self._get_shifts_per_roster(worker)
                self.model.Add(num_shifts_worked == shifts_per_roster)
        log.info("Enforcement of shifts per roster completed...")

    def _split_list(self, alist, wanted_parts=1):
        """Split list into parts.

        If length is odd then first half is smaller.

        """
        length = len(alist)
        return [
            alist[i * length // wanted_parts : (i + 1) * length // wanted_parts]
            for i in range(wanted_parts)
        ]

    def _enforce_balanced_shifts(self):
        """Enforce balanced shifts for each worker."""
        log.info("Enforcement of balanced shifts started...")
        for worker in self.workers:
            leave_dates = [
                leave.date for leave in self.leaves.filter(staff_member=worker)
            ]
            dates = [date for date in self.dates if date not in leave_dates]
            dates1, dates2 = self._split_list(dates, wanted_parts=2)
            num_shifts_worked1 = sum(
                self.shift_vars[(worker.id, role.id, date, timeslot.id)]
                for role in worker.roles.all()
                for date in dates1
                for timeslot in self.timeslots_lookup[date]
            )
            if worker.enforce_shifts_per_roster:
                shifts_per_roster = self._get_shifts_per_roster(worker)
                num_shifts = shifts_per_roster // 2
                self.model.Add(num_shifts_worked1 == num_shifts)
        log.info("Enforcement of balanced shifts completed...")

    def _enforce_staff_numbers(self):
        """Enforce staff numbers."""
        log.info("Enforcement of staff numbers started...")
        max_shift_size_lookup = {}
        min_shift_size_lookup = {}
        for shift_id in self.shiftrules:
            role_count_sizes = []
            for role_counts in self.shiftrules[shift_id]:
                role_count_sizes.append(sum(role_counts.values()))
            max_shift_size = max(role_count_sizes)
            min_shift_size = min(role_count_sizes)
            max_shift_size_lookup[shift_id] = max_shift_size
            min_shift_size_lookup[shift_id] = min_shift_size
        for timeslot in self.timeslots:
            max_timeslot_size = max_shift_size_lookup[timeslot.shift.id]
            min_timeslot_size = max_shift_size_lookup[timeslot.shift.id]
            num_staff_allocated = sum(
                self.shift_vars[(worker.id, role.id, timeslot.date, timeslot.id)]
                for worker in self.workers
                for role in worker.roles.all()
            )
            self.model.Add(num_staff_allocated >= min_timeslot_size)
            self.model.Add(num_staff_allocated <= max_timeslot_size)
        log.info("Enforcement of staff numbers completed...")

    def _maximise_staff_requests(self):
        """Maximise the number of satisfied staff requests."""
        log.info("Maximising of staff requests started...")
        self.model.Maximize(
            sum(
                self.shift_requests[n][d][s]
                * self.shift_vars[(worker.id, role.id, date, timeslot.id)]
                for n, worker in enumerate(self.workers)
                for role in worker.roles.all()
                for d, date in enumerate(self.dates)
                for s, timeslot in enumerate(self.timeslots_lookup[date])
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
        if solution_status not in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
            log.info("No feasible solution, raising exception...")
            raise SolutionNotFeasible("No feasible solutions.")

    def _populate_roster(self):
        """Populate roster."""
        log.info("Population of roster started...")
        shift_vars_for_current_period = {
            shift_var_key: self.shift_vars[shift_var_key]
            for shift_var_key in self.shift_vars
            if shift_var_key[2] in self.dates
        }
        TimeSlotStaffRelationship = TimeSlot.staff.through
        staff_to_add = []
        for shift_var_key in shift_vars_for_current_period:
            worker_id = shift_var_key[0]
            timeslot_id = shift_var_key[3]
            if self.solver.Value(self.shift_vars[shift_var_key]):
                staff_to_add.append(
                    TimeSlotStaffRelationship(
                        timeslot_id=timeslot_id,
                        customuser_id=worker_id,
                    )
                )
        TimeSlotStaffRelationship.objects.bulk_create(
            staff_to_add, ignore_conflicts=True
        )
        log.info("Population of roster completed...")

    def create(self):
        """Create roster as per constraints."""
        self._clear_existing_timeslots()
        self._create_timeslots()
        self._create_timeslots_lookup()
        self._collect_shift_requests()
        self._create_shift_vars()
        self._create_previous_shift_vars()
        self._exclude_leave_dates()
        self._enforce_one_shift_per_day()
        self._enforce_shifts_per_roster()
        self._collect_skill_mix_rules()
        self._create_intermediate_skill_mix_vars()
        self._enforce_one_skill_mix_rule_at_a_time()
        self._enforce_skill_mix_rules()
        self._enforce_balanced_shifts()
        self._precompute_invalid_shift_sequences()
        self._enforce_invalid_shift_sequences()
        self._enforce_staff_numbers()
        self._maximise_staff_requests()
        self._solve_roster()
        self._populate_roster()
        self.complete = True


def get_roster_by_staff(start_date):
    """Create data structures for roster grouped by staff."""
    num_days = Day.objects.count()
    dates = []
    for day in range(num_days):
        date = start_date + datetime.timedelta(days=day)
        date = date.date()
        dates.append(date)
    date_range = [
        start_date.date(),
        start_date.date() + datetime.timedelta(days=num_days - 1),
    ]
    roster = OrderedDict()
    workers = (
        get_user_model()
        .objects.all()
        .prefetch_related("roles")
        .order_by("roles__role_name", "last_name", "first_name")
    )
    timeslots = TimeSlot.objects.filter(date__range=date_range)
    for worker in workers:
        roster[f"{worker.last_name}, {worker.first_name}"] = OrderedDict()
        staff_roles = "".join(f"{role.role_name} " for role in worker.roles.all())

        roster[f"{worker.last_name}, {worker.first_name}"]["roles"] = staff_roles
        roster[f"{worker.last_name}, {worker.first_name}"]["shifts_per_roster"] = (
            worker.shifts_per_roster
        )

        for date in dates:
            roster[f"{worker.last_name}, {worker.first_name}"][date] = "X"
        worker_timeslots = [
            timeslot for timeslot in timeslots if worker in timeslot.staff.all()
        ]
        for timeslot in worker_timeslots:
            if roster[f"{worker.last_name}, {worker.first_name}"][timeslot.date] == "X":
                roster[f"{worker.last_name}, {worker.first_name}"][timeslot.date] = (
                    timeslot.shift.shift_type
                )

            else:
                roster[f"{worker.last_name}, {worker.first_name}"][timeslot.date] += (
                    f", {timeslot.shift.shift_type}"
                )

        worker_leave = worker.leave_set.filter(date__range=date_range)
        for leave in worker_leave:
            roster[f"{worker.last_name}, {worker.first_name}"][leave.date] = (
                leave.description
            )

    return dates, roster
