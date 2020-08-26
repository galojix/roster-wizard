"""Business logic testing."""

import pytest
import datetime

from django.contrib.auth import get_user_model

from rosters.models import (
    Shift,
    Day,
    DayGroup,
    DayGroupDay,
    ShiftRule,
    ShiftRuleRole,
    Role,
)
from rosters.logic import (
    RosterGenerator,
    SolutionNotFeasible,
    TooManyStaff,
)

pytestmark = pytest.mark.django_db


@pytest.fixture()
def init_feasible_db():
    """Initialise database."""
    staff_member1 = get_user_model().objects.create_user(
        username="one",
        last_name="One",
        first_name="One",
        available=True,
        shifts_per_roster=10,
    )
    staff_member2 = get_user_model().objects.create_user(
        username="two",
        last_name="Two",
        first_name="Two",
        available=True,
        shifts_per_roster=10,
    )
    role = Role.objects.create(role_name="RN")
    staff_member1.roles.add(role)
    staff_member2.roles.add(role)
    daygroup = DayGroup.objects.create(name="All Days")
    for i in range(1, 11):
        day = Day.objects.create(number=i)
        DayGroupDay.objects.create(daygroup=daygroup, day=day)
    shift = Shift.objects.create(
        shift_type="Early", daygroup=daygroup, max_staff=2
    )
    shift_rule = ShiftRule.objects.create(
        shift_rule_name="Early Option A", shift=shift
    )
    ShiftRuleRole.objects.create(shift_rule=shift_rule, role=role, count=2)


@pytest.fixture()
def init_infeasible_db():
    """Initialise database."""
    staff_member1 = get_user_model().objects.create_user(
        username="one",
        last_name="One",
        first_name="One",
        available=True,
        shifts_per_roster=10,
    )
    staff_member2 = get_user_model().objects.create_user(
        username="two",
        last_name="Two",
        first_name="Two",
        available=True,
        shifts_per_roster=9,
    )
    role = Role.objects.create(role_name="RN")
    staff_member1.roles.add(role)
    staff_member2.roles.add(role)
    daygroup = DayGroup.objects.create(name="All Days")
    for i in range(1, 11):
        day = Day.objects.create(number=i)
        DayGroupDay.objects.create(daygroup=daygroup, day=day)
    shift = Shift.objects.create(
        shift_type="Early", daygroup=daygroup, max_staff=2
    )
    shift_rule = ShiftRule.objects.create(
        shift_rule_name="Early Option A", shift=shift
    )
    ShiftRuleRole.objects.create(shift_rule=shift_rule, role=role, count=2)


@pytest.fixture()
def init_too_many_staff_db():
    """Initialise database."""
    staff_member1 = get_user_model().objects.create_user(
        username="one",
        last_name="One",
        first_name="One",
        available=True,
        shifts_per_roster=10,
    )
    staff_member2 = get_user_model().objects.create_user(
        username="two",
        last_name="Two",
        first_name="Two",
        available=True,
        shifts_per_roster=11,
    )
    role = Role.objects.create(role_name="RN")
    staff_member1.roles.add(role)
    staff_member2.roles.add(role)
    daygroup = DayGroup.objects.create(name="All Days")
    for i in range(1, 11):
        day = Day.objects.create(number=i)
        DayGroupDay.objects.create(daygroup=daygroup, day=day)
    shift = Shift.objects.create(
        shift_type="Early", daygroup=daygroup, max_staff=2
    )
    shift_rule = ShiftRule.objects.create(
        shift_rule_name="Early Option A", shift=shift
    )
    ShiftRuleRole.objects.create(shift_rule=shift_rule, role=role, count=2)


def test_feasible_roster_generation(init_feasible_db):
    """Test feasible roster generation."""
    roster = RosterGenerator(start_date=datetime.datetime.now())
    roster.create()
    assert roster.complete


def test_infeasible_roster_generation(init_infeasible_db):
    """Test infeasible roster generation."""
    roster = RosterGenerator(start_date=datetime.datetime.now())
    with pytest.raises(SolutionNotFeasible):
        roster.create()


def test_too_many_staff_roster_generation(init_too_many_staff_db):
    """Test too many staff roster generation."""
    roster = RosterGenerator(start_date=datetime.datetime.now())
    with pytest.raises(TooManyStaff):
        roster.create()
