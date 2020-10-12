"""View Testing."""

import pytest
import datetime

from django.urls import reverse
from django.test import SimpleTestCase

from rosters.models import Day

pytestmark = pytest.mark.django_db


def test_day_detail_view(init_feasible_db, client):
    """Test day detail view."""
    client.login(username="temporary", password="temporary")
    day = Day.objects.get(number=1)
    response = client.get(reverse("day_detail", kwargs={"pk": day.id}))
    assert response.status_code == 200
    assert "Day: 1" in response.rendered_content
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
        response, "/accounts/login/?next=/rosters/roster_by_staff/"
    )


def test_generate_roster_view(init_db, client):
    """Test generate roster view."""
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("generate_roster"))
    assert response.status_code == 200
    assert "Generate New Roster:" in response.rendered_content
    assert "generate_roster.html" in [t.name for t in response.templates]


def test_home_view(init_feasible_db, client):
    """Test home page view."""
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("home"))
    assert response.status_code == 200
    assert "Automatically generated rosters" in response.rendered_content
    assert "home.html" in [t.name for t in response.templates]


def test_leave_list_view(init_feasible_db, client):
    """Test leave list view."""
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("leave_list"))
    assert response.status_code == 200
    assert "Leave:" in response.rendered_content
    assert "leave_list.html" in [t.name for t in response.templates]


def test_generate_roster_view_post(init_db, client, mocker):
    """Test generate roster view post."""
    client.login(username="temporary", password="temporary")
    mocker.patch("rosters.tasks.generate_roster.delay")
    response = client.post(
        reverse("generate_roster"), {"start_date": datetime.datetime.now()}
    )
    assert response.status_code == 302
    assert "/rosters/roster_status/" in response.url
