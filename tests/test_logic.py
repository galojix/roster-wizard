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
    StaffRequest,
    StaffRule,
    StaffRuleShift,
    Leave,
)
from rosters.logic import (
    RosterGenerator,
    SolutionNotFeasible,
    TooManyStaff,
)

from rosters.tasks import generate_roster

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
    staff_member3 = get_user_model().objects.create_user(
        username="three",
        last_name="Three",
        first_name="Three",
        available=True,
        shifts_per_roster=10,
    )
    staff_member4 = get_user_model().objects.create_user(
        username="four",
        last_name="Four",
        first_name="Four",
        available=True,
        shifts_per_roster=10,
    )
    staff_member5 = get_user_model().objects.create_user(
        username="deficit",
        last_name="deficit",
        first_name="deficit",
        available=True,
        shifts_per_roster=0,
    )
    rn = Role.objects.create(role_name="RN")
    srn = Role.objects.create(role_name="SRN")
    jrn = Role.objects.create(role_name="JRN")
    staff_member1.roles.add(rn)
    staff_member2.roles.add(rn)
    staff_member3.roles.add(srn)
    staff_member4.roles.add(jrn)
    staff_member5.roles.add(rn)
    staff_member5.roles.add(srn)
    staff_member5.roles.add(jrn)
    daygroup = DayGroup.objects.create(name="All Days")
    for i in range(1, 15):
        day = Day.objects.create(number=i)
        DayGroupDay.objects.create(daygroup=daygroup, day=day)
    early_shift = Shift.objects.create(
        shift_type="Early", daygroup=daygroup, max_staff=2
    )
    late_shift = Shift.objects.create(
        shift_type="Late", daygroup=daygroup, max_staff=1
    )
    early_shiftrule1 = ShiftRule.objects.create(
        shiftrule_name="Early Option A", shift=early_shift
    )
    ShiftRuleRole.objects.create(shiftrule=early_shiftrule1, role=rn, count=2)
    early_shiftrule2 = ShiftRule.objects.create(
        shiftrule_name="Early Option B", shift=early_shift
    )
    ShiftRuleRole.objects.create(shiftrule=early_shiftrule2, role=rn, count=1)
    ShiftRuleRole.objects.create(shiftrule=early_shiftrule2, role=jrn, count=1)
    early_shiftrule3 = ShiftRule.objects.create(
        shiftrule_name="Early Option C", shift=early_shift
    )
    ShiftRuleRole.objects.create(shiftrule=early_shiftrule3, role=srn, count=1)
    ShiftRuleRole.objects.create(shiftrule=early_shiftrule3, role=jrn, count=1)
    late_shiftrule1 = ShiftRule.objects.create(
        shiftrule_name="Late Option A", shift=late_shift
    )
    ShiftRuleRole.objects.create(shiftrule=late_shiftrule1, role=srn, count=1)
    late_shiftrule2 = ShiftRule.objects.create(
        shiftrule_name="Late Option B", shift=late_shift
    )
    ShiftRuleRole.objects.create(shiftrule=late_shiftrule2, role=rn, count=1)
    StaffRequest.objects.create(
        priority=1,
        like=True,
        date=datetime.datetime.now(),
        shift=early_shift,
        staff_member=staff_member1,
    )
    staff_rule1 = StaffRule.objects.create(
        staffrule_name="No Early after Late", daygroup=daygroup
    )
    staff_rule1.staff.add(staff_member1)
    staff_rule1.staff.add(staff_member2)
    StaffRuleShift.objects.create(
        shift=late_shift, staffrule=staff_rule1, position=1
    )
    StaffRuleShift.objects.create(
        shift=early_shift, staffrule=staff_rule1, position=2
    )
    Leave.objects.create(
        date=datetime.datetime.now(),
        description="Leave",
        staff_member=staff_member2,
    )


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
    shiftrule = ShiftRule.objects.create(
        shiftrule_name="Early Option A", shift=shift
    )
    ShiftRuleRole.objects.create(shiftrule=shiftrule, role=role, count=2)


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
    shiftrule = ShiftRule.objects.create(
        shiftrule_name="Early Option A", shift=shift
    )
    ShiftRuleRole.objects.create(shiftrule=shiftrule, role=role, count=2)


def test_feasible_roster_generation(init_feasible_db):
    """Test feasible roster generation."""
    task = generate_roster.delay(start_date=datetime.datetime.now())
    result = task.get()
    # roster = RosterGenerator(start_date=datetime.datetime.now())
    # roster.create()
    # assert roster.complete
    assert result.status == "SUCCESS"


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
