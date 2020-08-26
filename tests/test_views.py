"""View Testing."""

import pytest

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase

from rosters.models import Day

pytestmark = pytest.mark.django_db


@pytest.fixture()
def init_db():
    """Initialise database."""
    get_user_model().objects.create_user(
        username="temporary",
        password="temporary",
        last_name="Joey",
        first_name="Smith",
        available=True,
        shifts_per_roster=10,
    )


def test_day_detail_view(init_db, client):
    """Test day detail view."""
    day = Day.objects.create(number=5)
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("day_detail", kwargs={"pk": day.id}))
    assert response.status_code == 200
    assert "Day: 5" in response.rendered_content
    assert "day_detail.html" in [t.name for t in response.templates]


def test_roster_list_view(init_db, client):
    """Test roster list view."""
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("roster_by_staff"))
    assert response.status_code == 200
    assert "Roster By Staff:" in response.rendered_content
    assert "roster_by_staff.html" in [t.name for t in response.templates]


def test_roster_list_redirect_if_not_logged_in(client):
    """Test roster list view redirects if not logged in."""
    response = client.get(reverse("roster_by_staff"))
    SimpleTestCase().assertRedirects(
        response, "/users/login/?next=/rosters/roster_by_staff/"
    )
