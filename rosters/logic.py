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


def generate_roster(start_date):
    """Generate roster as per constraints."""
    nurses = get_user_model().objects.filter(available=True)
    shifts = Shift.objects.all().order_by("shift_type")
    num_days = Day.objects.count()

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
    for day in range(1, num_days + 1):
        dates.append(date)
        for shift in shifts:
            day_group_days = shift.day_group.daygroupday_set.all()
            for day_group_day in day_group_days:
                if day_group_day.day.number == day:
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
    log.info("Creating shift variables...")
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
    log.info("Shift variables created...")
    log.debug(shift_vars.keys())

    # Create shift variables and fixed constraints
    # for previous roster period
    log.info("Creating shift variables for previous period...")
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
    log.info("Shift variables for previous period created...")

    # Exclude leave dates from roster
    log.info("Excluding leave dates...")
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
    log.info("Leave dates excluded...")

    # Enforce shift sequences / staff rules
    # Need to look at previous roster period also
    log.info("Adding shift sequences...")
    extended_dates = []
    date = start_date.date() - datetime.timedelta(days=num_days)
    for day in range(2 * num_days):
        extended_dates.append(date)
        date += datetime.timedelta(days=1)
    timeslot_ids = {}
    for date in extended_dates:
        timeslot_ids[date] = {}
        for shift in shifts:
            try:
                timeslot_ids[date][shift] = TimeSlot.objects.get(
                    date=date, shift=shift
                ).id
            except TimeSlot.DoesNotExist:
                continue
    for nurse in nurses:
        roles = nurse.roles.all()
        for staff_rule in nurse.staffrule_set.all():
            invalid_shift_sequence = OrderedDict()
            staff_rule_shifts = staff_rule.staffruleshift_set.all().order_by(
                "position"
            )
            for staff_rule_shift in staff_rule_shifts:
                invalid_shift_sequence.setdefault(
                    staff_rule_shift.position, []
                ).append(staff_rule_shift.shift)
            sequence_size = len(invalid_shift_sequence)
            sequence_days = [
                day_group_day.day.number
                for day_group_day in staff_rule.day_group.daygroupday_set.all()
            ]
            shift_vars_in_seq = []
            for date in extended_dates:
                shift_vars_in_seq = []
                for day_num in invalid_shift_sequence:
                    for invalid_shift in invalid_shift_sequence[day_num]:
                        day_to_test = date + datetime.timedelta(
                            days=day_num - 1
                        )
                        delta = (day_to_test - start_date.date()).days

                        # Skip if day not in day group for sequence
                        if delta < 0:
                            day_group_day_num = delta + num_days + 1
                        else:
                            day_group_day_num = delta + 1
                        if day_group_day_num not in sequence_days:
                            break

                        for role in roles:
                            try:
                                shift_vars_in_seq.append(
                                    shift_vars[
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
                model.Add(sum(shift_vars_in_seq) < sequence_size)
    log.info("Shift sequences added...")

    # Collect shift rules into friendly structure
    log.info("Collecting skill mix rules...")
    shift_rules = {}
    for shift in shifts:
        shift_rules[shift.id] = []
        shiftrules = ShiftRule.objects.filter(shift=shift)
        for shiftrule in shiftrules:
            shiftruleroles = shiftrule.shiftrulerole_set.all()
            role_count = {}
            for role in Role.objects.all():
                role_count[role.id] = 0
            for shiftrulerole in shiftruleroles:
                role_count[shiftrulerole.role.id] = shiftrulerole.count
            shift_rules[shift.id].append(role_count)

    log.info("Skill mix rules collected...")
    log.debug(shift_rules)

    # Intermediate shift rule variables
    log.info("Creating intermediate variables...")
    intermediate_vars = {
        (timeslot.id, rule_num): model.NewBoolVar(f"t{timeslot.id}r{rule_num}")
        for timeslot in timeslots
        for rule_num, rule in enumerate(shift_rules[timeslot.shift.id])
    }
    log.info("Intermediate vars created...")
    log.debug(intermediate_vars)

    # Only one shift rule at a time can be satisfied
    log.info("Adding intermediate variable constraints...")
    for timeslot in timeslots:
        if len(shift_rules[timeslot.shift.id]) >= 1:
            model.Add(
                sum(
                    intermediate_vars[(timeslot.id, rule_num)]
                    for rule_num, rule in enumerate(
                        shift_rules[timeslot.shift.id]
                    )
                )
                == 1
            )
    log.info("Intermediate variable constraints added...")

    # Enforce one shift rule per shift per timeslot
    log.info("Enforcing skill mix constraints...")
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
                                for nurse in nurses.filter(roles__id=role_id)
                            )
                            == role_count
                        ).OnlyEnforceIf(
                            intermediate_vars[(timeslot.id, rule_num)]
                        )
    log.info("Skill mix constraints enforced...")

    # Assign at most one shift per day per nurse
    log.info("Restrict staff to one shift per day...")
    for nurse in nurses:
        for date in dates:
            if nurse.shifts_per_roster != 0:  # Zero means unlimited shifts
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
    log.info("Staff restricted to one shift per day...")

    # Enforce shifts per roster for each nurse
    log.info("Enforce shifts per roster...")
    for nurse in nurses:
        num_shifts_worked = sum(
            shift_vars[(nurse.id, role.id, date, timeslot.id)]
            for role in nurse.roles.all()
            for date in dates
            for timeslot in TimeSlot.objects.filter(date=date).order_by(
                "shift__shift_type"
            )
        )
        if nurse.shifts_per_roster != 0:  # Zero means unlimited shifts
            model.Add(nurse.shifts_per_roster == num_shifts_worked)
    log.info("Shifts per roster enforced...")

    # Maximise the number of satisfied shift requests
    log.info("Maximising shift requests...")
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
    log.info("Shift requests maximised.")

    # Create the solver and solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 180
    log.info("Solver started...")
    solution_status = solver.Solve(model)
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

    # for value in intermediate_vars.values():
    #     print(value, solver.Value(value))

    log.info("Populating roster...")
    for d, date in enumerate(dates):
        # log.info(f"Day {d}:")
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
                            # log.info(
                            #     f"*** Request Successful *** "
                            #     f"{nurse.last_name}, {nurse.first_name}"
                            #     f" requested shift"
                            #     f" {timeslot.shift.shift_type}"
                            #     f" and was assigned."
                            # )
                            TimeSlot.objects.get(
                                date=date, shift=timeslot.shift
                            ).staff.add(nurse)
                        else:
                            # log.info(
                            #     f"{nurse.last_name}, {nurse.first_name}"
                            #     f" did not request shift"
                            #     f" {timeslot.shift.shift_type}"
                            #     f" and was assigned."
                            # )
                            TimeSlot.objects.get(
                                date=date, shift=timeslot.shift
                            ).staff.add(nurse)
                    # else:
                    #     if shift_requests[n][d][s] >= 1:
                    #         log.info(
                    #             f"*** Request Failed *** "
                    #             f"{nurse.last_name}, {nurse.first_name}"
                    #             f" requested shift"
                    #             f" {timeslot.shift.shift_type}"
                    #             f" but was not assigned."
                    #         )
    log.info("Roster populated...")


def get_roster_by_staff(start_date):
    """Create data structures for roster grouped by staff."""
    dates = []
    roster = OrderedDict()
    nurses = get_user_model().objects.all().order_by("last_name")
    num_days = Day.objects.count()
    for nurse in nurses.order_by(
        "roles__role_name", "last_name", "first_name"
    ):
        roster[nurse.last_name + ", " + nurse.first_name] = OrderedDict()
        staff_roles = ""
        for role in nurse.roles.all().order_by("role_name"):
            staff_roles += role.role_name + " "
        roster[nurse.last_name + ", " + nurse.first_name][
            "roles"
        ] = staff_roles
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
                roster[nurse.last_name + ", " + nurse.first_name][date] = "X"
            except TimeSlot.MultipleObjectsReturned:
                timeslots = TimeSlot.objects.filter(date=date, staff=nurse.id)
                roster[nurse.last_name + ", " + nurse.first_name][date] = ""
                for timeslot in timeslots:
                    roster[nurse.last_name + ", " + nurse.first_name][
                        date
                    ] += (timeslot.shift.shift_type + " ")
    return dates, roster
