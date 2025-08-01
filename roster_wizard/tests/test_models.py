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
    SkillMixRule,
    SkillMixRuleRole,
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
        f"{leave.staff_member.last_name},{leave.staff_member.first_name} {leave.date}"
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


def test_skillmixrule_get_absolute_url(init_feasible_db):
    """Test skill mix rule  get_absolute_url custom method."""
    skillmixrule = SkillMixRule.objects.first()
    # This will also fail if the urlconf is not defined.
    assert (
        skillmixrule.get_absolute_url() == f"/rosters/skillmixrule/{skillmixrule.id}/"
    )


def test_skillmixrulerole_object_name(init_feasible_db):
    """Test skillmixrulerole object name."""
    skillmixrulerole = SkillMixRuleRole.objects.first()
    expected_object_name = (
        f"{skillmixrulerole.skillmixrule.skillmixrule_name} "
        f"{skillmixrulerole.role.role_name}:"
        f"{skillmixrulerole.count}"
    )
    assert expected_object_name == str(skillmixrulerole)


def test_shiftsequence_object_name(init_feasible_db):
    """Test shiftsequence object name."""
    shiftsequence = ShiftSequence.objects.first()
    expected_object_name = f"{shiftsequence.shiftsequence_name}"
    assert expected_object_name == str(shiftsequence)


def test_shiftsequence_get_absolute_url(init_feasible_db):
    """Test shiftsequence day get_absolute_url custom method."""
    shiftsequence = ShiftSequence.objects.first()
    # This will also fail if the urlconf is not defined.
    assert (
        shiftsequence.get_absolute_url()
        == f"/rosters/shiftsequence/{shiftsequence.id}/"
    )


def test_shiftsequenceshift_object_name(init_feasible_db):
    """Test shiftsequenceshift object name."""
    shiftsequenceshift = ShiftSequenceShift.objects.first()
    expected_object_name = (
        f"{shiftsequenceshift.shiftsequence.shiftsequence_name}:"
        f"{shiftsequenceshift.shift.shift_type}:"
        f"{shiftsequenceshift.position}"
    )
    assert expected_object_name == str(shiftsequenceshift)


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
        f"{staffrequest.staff_member.last_name},"
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
