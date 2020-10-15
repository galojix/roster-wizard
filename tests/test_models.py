"""Model testing."""
import pytest

from rosters.models import Leave, Role, DayGroup

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
        f"{leave.staff_member.last_name}, "
        f"{leave.staff_member.first_name} "
        f"{leave.date}"
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
