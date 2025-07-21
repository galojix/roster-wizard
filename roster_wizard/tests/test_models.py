"""Model testing."""

import pytest

from users.models import CustomUser
from rosters.models import (
    Leave,
    Role,
    DayGroup,
    Day,
    DayGroupDay,
    Shift,
    ShiftRule,
    ShiftRuleRole,
    ShiftSequence,
    ShiftSequenceShift,
    TimeSlot,
    StaffRequest,
)

pytestmark = pytest.mark.django_db


def test_leave_description_max_length(init_feasible_db):
    """Test leave description maximum length."""
    leave = Leave.objects.first()
    max_length = leave._meta.get_field("description").max_length
    assert max_length == 15


def test_leave_object_name(init_feasible_db):
    """Test leave object name."""
    leave = Leave.objects.first()
    expected_object_name = (
        f"{leave.staff_member.last_name}, {leave.staff_member.first_name} {leave.date}"
    )
    assert expected_object_name == str(leave)


def test_leave_get_absolute_url(init_feasible_db):
    """Test leave get_absolute_url custom method."""
    leave = Leave.objects.first()
    # This will also fail if the urlconf is not defined.
    assert leave.get_absolute_url() == f"/rosters/leave/{leave.id}/"


def test_role_get_absolute_url(init_feasible_db):
    """Test role get_absolute_url custom method."""
    role = Role.objects.first()
    # This will also fail if the urlconf is not defined.
    assert role.get_absolute_url() == f"/rosters/role/{role.id}/"


def test_daygroup_object_name(init_feasible_db):
    """Test daygroup object name."""
    daygroup = DayGroup.objects.first()
    expected_object_name = f"{daygroup.name}"
    assert expected_object_name == str(daygroup)


def test_day_get_absolute_url(init_feasible_db):
    """Test day get_absolute_url custom method."""
    day = Day.objects.first()
    # This will also fail if the urlconf is not defined.
    assert day.get_absolute_url() == f"/rosters/day/{day.id}/"


def test_day_object_name(init_feasible_db):
    """Test day object name."""
    day = Day.objects.first()
    expected_object_name = f"{day.number}"
    assert expected_object_name == str(day)


def test_daygroupday_object_name(init_feasible_db):
    """Test daygroupday object name."""
    daygroupday = DayGroupDay.objects.first()
    expected_object_name = f"{daygroupday.daygroup.name}{daygroupday.day.number}"
    assert expected_object_name == str(daygroupday)


def test_shift_get_absolute_url(init_feasible_db):
    """Test shift get_absolute_url custom method."""
    shift = Shift.objects.first()
    # This will also fail if the urlconf is not defined.
    assert shift.get_absolute_url() == f"/rosters/shift/{shift.id}/"


def test_shiftrule_get_absolute_url(init_feasible_db):
    """Test shiftrule get_absolute_url custom method."""
    shiftrule = ShiftRule.objects.first()
    # This will also fail if the urlconf is not defined.
    assert shiftrule.get_absolute_url() == f"/rosters/shiftrule/{shiftrule.id}/"


def test_shiftrulerole_object_name(init_feasible_db):
    """Test shiftrulerole object name."""
    shiftrulerole = ShiftRuleRole.objects.first()
    expected_object_name = (
        f"{shiftrulerole.shiftrule.shiftrule_name} "
        f"{shiftrulerole.role.role_name}:"
        f"{shiftrulerole.count}"
    )
    assert expected_object_name == str(shiftrulerole)


def test_staffrule_object_name(init_feasible_db):
    """Test staffrule object name."""
    staffrule = ShiftSequence.objects.first()
    expected_object_name = f"{staffrule.staffrule_name}"
    assert expected_object_name == str(staffrule)


def test_staffrule_get_absolute_url(init_feasible_db):
    """Test staffrule day get_absolute_url custom method."""
    staffrule = ShiftSequence.objects.first()
    # This will also fail if the urlconf is not defined.
    assert staffrule.get_absolute_url() == f"/rosters/staffrule/{staffrule.id}/"


def test_staffruleshift_object_name(init_feasible_db):
    """Test staffruleshift object name."""
    staffruleshift = ShiftSequenceShift.objects.first()
    expected_object_name = (
        f"{staffruleshift.staffrule.staffrule_name}:"
        f"{staffruleshift.shift.shift_type}:"
        f"{staffruleshift.position}"
    )
    assert expected_object_name == str(staffruleshift)


def test_timeslot_object_name(init_feasible_db):
    """Test timeslot object name."""
    timeslot = TimeSlot.objects.first()
    expected_object_name = f"{timeslot.date}:{timeslot.shift.shift_type}"
    assert expected_object_name == str(timeslot)


def test_timeslot_get_absolute_url(init_feasible_db):
    """Test timeslot get_absolute_url custom method."""
    timeslot = TimeSlot.objects.first()
    # This will also fail if the urlconf is not defined.
    assert timeslot.get_absolute_url() == "/rosters/timeslot/"


def test_staffrequest_object_name(init_feasible_db):
    """Test staffrequest object name."""
    staffrequest = StaffRequest.objects.first()
    expected_object_name = (
        f"{staffrequest.staff_member.last_name}, "
        f"{staffrequest.staff_member.first_name} "
        f"{staffrequest.shift.shift_type} "
        f"{staffrequest.date}"
    )
    assert expected_object_name == str(staffrequest)


def test_staffrequest_get_absolute_url(init_feasible_db):
    """Test staffrequest get_absolute_url custom method."""
    staffrequest = StaffRequest.objects.first()
    # This will also fail if the urlconf is not defined.
    assert (
        staffrequest.get_absolute_url() == f"/rosters/staffrequest/{staffrequest.id}/"
    )


def test_customuser_object_name(init_feasible_db):
    """Test customuser object name."""
    customuser = CustomUser.objects.first()
    expected_object_name = f"{customuser.last_name},{customuser.first_name}"
    assert expected_object_name == str(customuser)


def test_customuser_get_absolute_url(init_feasible_db):
    """Test customuser_get_absolute_url custom method."""
    customuser = CustomUser.objects.first()
    # This will also fail if the urlconf is not defined.
    assert customuser.get_absolute_url() == f"/users/customuser/{customuser.id}/"
