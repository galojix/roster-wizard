"""Model testing."""

import pytest
import datetime

from django.contrib.auth import get_user_model

from rosters.models import Leave

pytestmark = pytest.mark.django_db


@pytest.fixture()
def init_db():
    """Initialise database."""
    staff_member = get_user_model().objects.create_user(
        username="temporary",
        password="temporary",
        last_name="Joey",
        first_name="Smith",
        available=True,
        shifts_per_roster=10,
    )
    Leave.objects.create(
        date=datetime.datetime.now().date(),
        description="Test leave",
        staff_member=staff_member,
    )


def test_leave_description_max_length(init_db):
    """Test leave description maximum length."""
    leave = Leave.objects.first()
    max_length = leave._meta.get_field("description").max_length
    assert max_length == 15


def test_leave_object_name(init_db):
    """Test leave object name."""
    leave = Leave.objects.first()
    expected_object_name = (
        f"{leave.staff_member.last_name}, "
        f"{leave.staff_member.first_name} "
        f"{leave.date}"
    )
    assert expected_object_name == str(leave)


def test_leave_get_absolute_url(init_db):
    """Test leave get_absolute_url custom method."""
    leave = Leave.objects.first()
    # This will also fail if the urlconf is not defined.
    assert leave.get_absolute_url() == f"/rosters/leave/{leave.id}/"
