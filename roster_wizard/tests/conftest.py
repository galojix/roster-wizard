"""Shared fixtures."""

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
    ShiftSequence,
    StaffRuleShift,
    Leave,
    TimeSlot,
)
from rosters.logic import RosterGenerator

pytestmark = pytest.mark.django_db


@pytest.fixture()
def init_db():
    """Initialise database."""
    get_user_model().objects.create_user(
        username="temporary",
        password="temporary",
        email="temporrary@fred.com",
        last_name="Joey",
        first_name="Smith",
        available=False,
        shifts_per_roster=10,
        is_superuser=True,
    )


@pytest.fixture()
def init_feasible_db(init_db):
    """Initialise database."""
    staff_member1 = get_user_model().objects.create_user(
        username="one",
        password="temporary",
        last_name="One",
        first_name="One",
        email="one@fred.com",
        available=True,
        shifts_per_roster=10,
    )
    staff_member2 = get_user_model().objects.create_user(
        username="two",
        password="temporary",
        last_name="Two",
        first_name="Two",
        email="two@fred.com",
        available=True,
        shifts_per_roster=10,
    )
    staff_member3 = get_user_model().objects.create_user(
        username="three",
        password="temporary",
        last_name="Three",
        first_name="Three",
        email="three@fred.com",
        available=True,
        shifts_per_roster=10,
    )
    staff_member4 = get_user_model().objects.create_user(
        username="four",
        password="temporary",
        last_name="Four",
        first_name="Four",
        email="four@fred.com",
        available=True,
        shifts_per_roster=10,
    )
    staff_member5 = get_user_model().objects.create_user(
        username="casual",
        password="temporary",
        last_name="casual",
        first_name="casual",
        email="casual@fred.com",
        available=True,
        shifts_per_roster=0,
        enforce_shifts_per_roster=False,
        enforce_one_shift_per_day=False,
    )
    staff_member6 = get_user_model().objects.create_user(
        username="six",
        password="temporary",
        last_name="Six",
        first_name="Six",
        email="six@fred.com",
        available=True,
        max_shifts=False,
        shifts_per_roster=1,
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
    staff_member6.roles.add(jrn)
    daygroup = DayGroup.objects.create(name="All Days")
    for i in range(1, 15):
        day = Day.objects.create(number=i)
        DayGroupDay.objects.create(daygroup=daygroup, day=day)
    early_shift = Shift.objects.create(
        shift_type="Early",
        daygroup=daygroup,
    )
    late_shift = Shift.objects.create(
        shift_type="Late",
        daygroup=daygroup,
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
    StaffRequest.objects.create(
        priority=2,
        like=True,
        date=datetime.datetime.now(),
        shift=late_shift,
        staff_member=staff_member1,
    )
    StaffRequest.objects.create(
        priority=100,
        like=True,
        date=datetime.datetime.now() + datetime.timedelta(days=1),
        shift=late_shift,
        staff_member=staff_member1,
    )
    StaffRequest.objects.create(
        priority=1,
        like=False,
        date=datetime.datetime.now() + datetime.timedelta(days=1),
        shift=late_shift,
        staff_member=staff_member1,
    )
    StaffRequest.objects.create(
        priority=10,
        like=False,
        date=datetime.datetime.now() + datetime.timedelta(days=1),
        shift=early_shift,
        staff_member=staff_member1,
    )
    StaffRequest.objects.create(
        priority=10,
        like=False,
        date=datetime.datetime.now() + datetime.timedelta(days=2),
        shift=early_shift,
        staff_member=staff_member1,
    )
    StaffRequest.objects.create(
        priority=10,
        like=False,
        date=datetime.datetime.now() + datetime.timedelta(days=2),
        shift=late_shift,
        staff_member=staff_member1,
    )
    StaffRequest.objects.create(
        priority=10,
        like=False,
        date=datetime.datetime.now() + datetime.timedelta(days=3),
        shift=early_shift,
        staff_member=staff_member1,
    )
    StaffRequest.objects.create(
        priority=10,
        like=False,
        date=datetime.datetime.now() + datetime.timedelta(days=3),
        shift=late_shift,
        staff_member=staff_member1,
    )
    StaffRequest.objects.create(
        priority=10,
        like=False,
        date=datetime.datetime.now() + datetime.timedelta(days=4),
        shift=early_shift,
        staff_member=staff_member1,
    )
    StaffRequest.objects.create(
        priority=10,
        like=False,
        date=datetime.datetime.now() + datetime.timedelta(days=4),
        shift=late_shift,
        staff_member=staff_member1,
    )
    staff_rule1 = ShiftSequence.objects.create(
        staffrule_name="No Early after Late", daygroup=daygroup
    )
    staff_rule1.staff.add(staff_member1)
    staff_rule1.staff.add(staff_member2)
    StaffRuleShift.objects.create(shift=late_shift, staffrule=staff_rule1, position=1)
    StaffRuleShift.objects.create(shift=early_shift, staffrule=staff_rule1, position=2)
    StaffRuleShift.objects.create(staffrule=staff_rule1, position=3)
    Leave.objects.create(
        date=datetime.datetime.now(),
        description="Leave",
        staff_member=staff_member2,
    )
    for i in range(0, 13):
        Leave.objects.create(
            date=datetime.datetime.now() + datetime.timedelta(days=i),
            description="Leave",
            staff_member=staff_member6,
        )
    timeslot = TimeSlot.objects.create(
        date=datetime.datetime.now() - datetime.timedelta(days=1),
        shift=early_shift,
    )
    timeslot.staff.set([staff_member1, staff_member2])


@pytest.fixture()
def init_infeasible_db(init_db):
    """Initialise database."""
    staff_member1 = get_user_model().objects.create_user(
        username="one",
        password="temporary",
        last_name="One",
        first_name="One",
        email="one@fred.com",
        available=True,
        shifts_per_roster=10,
    )
    staff_member2 = get_user_model().objects.create_user(
        username="two",
        password="temporary",
        last_name="Two",
        first_name="Two",
        email="two@fred.com",
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
        shift_type="Early",
        daygroup=daygroup,
    )
    shiftrule = ShiftRule.objects.create(shiftrule_name="Early Option A", shift=shift)
    ShiftRuleRole.objects.create(shiftrule=shiftrule, role=role, count=2)


@pytest.fixture()
def init_too_many_staff_db(init_db):
    """Initialise database."""
    staff_member1 = get_user_model().objects.create_user(
        username="one",
        password="temporary",
        last_name="One",
        first_name="One",
        email="one@fred.com",
        available=True,
        shifts_per_roster=10,
    )
    staff_member2 = get_user_model().objects.create_user(
        username="two",
        password="temporary",
        last_name="Two",
        first_name="Two",
        email="two@fred.com",
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
        shift_type="Early",
        daygroup=daygroup,
    )
    shiftrule = ShiftRule.objects.create(shiftrule_name="Early Option A", shift=shift)
    ShiftRuleRole.objects.create(shiftrule=shiftrule, role=role, count=2)


@pytest.fixture()
def init_roster_db(init_feasible_db):
    """Initialise a database with a populated roster."""
    roster = RosterGenerator(start_date=datetime.datetime.now())
    roster.create()
    assert roster.complete
