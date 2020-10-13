"""View Testing."""

import pytest
import datetime

from django.urls import reverse
from django.test import SimpleTestCase
from django.contrib.auth import get_user_model

from rosters.models import Day
from rosters.views import generate_roster, AsyncResult
from rosters.logic import SolutionNotFeasible, TooManyStaff

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


def test_generate_roster_view_post_feasible(init_db, client, mocker):
    """Test generate roster view post."""
    client.login(username="temporary", password="temporary")
    delay_result = mocker.stub(name="delay_result")
    delay_result.task_id = 12345
    mocker.patch.object(generate_roster, "delay", return_value=delay_result)
    response = client.post(
        reverse("generate_roster"), {"start_date": datetime.datetime.now()}
    )
    assert response.status_code == 302
    assert "/rosters/roster_status/" in response.url


def test_roster_generation_status_view_feasible(init_db, client, mocker):
    """Test roster generation status view."""
    client.login(username="temporary", password="temporary")
    mocker.patch.object(AsyncResult, "ready", return_value=True)
    mocker.patch.object(
        AsyncResult, "get", return_value="Roster is complete..."
    )
    response = client.get(reverse("roster_generation_status", args=("12345",)))
    assert response.status_code == 200
    assert "Roster is complete..." in str(response.getvalue())
    assert "roster_generation_status.html" in [
        t.name for t in response.templates
    ]


def test_roster_generation_status_view_infeasible(init_db, client, mocker):
    """Test roster generation status view."""
    client.login(username="temporary", password="temporary")
    mocker.patch.object(AsyncResult, "ready", return_value=True)
    mocker.patch.object(AsyncResult, "get", side_effect=SolutionNotFeasible)
    response = client.get(reverse("roster_generation_status", args=("12345",)))
    assert response.status_code == 200
    assert (
        "Could not generate roster, try putting more staff on leave or changing rules..."
        in str(response.getvalue())
    )
    assert "roster_generation_status.html" in [
        t.name for t in response.templates
    ]


def test_roster_generation_status_view_too_many_staff(init_db, client, mocker):
    """Test roster generation status view."""
    client.login(username="temporary", password="temporary")
    mocker.patch.object(AsyncResult, "ready", return_value=True)
    mocker.patch.object(AsyncResult, "get", side_effect=TooManyStaff)
    response = client.get(reverse("roster_generation_status", args=("12345",)))
    assert response.status_code == 200
    assert (
        "There are too many staff available, put more staff on leave..."
        in str(response.getvalue())
    )
    assert "roster_generation_status.html" in [
        t.name for t in response.templates
    ]


def test_roster_generation_status_view_processing(init_db, client, mocker):
    """Test roster generation status view."""
    client.login(username="temporary", password="temporary")
    mocker.patch.object(AsyncResult, "ready", return_value=False)
    response = client.get(reverse("roster_generation_status", args=("12345",)))
    assert response.status_code == 200
    assert "Processing..." in str(response.getvalue())
    assert "roster_generation_status.html" in [
        t.name for t in response.templates
    ]


def test_leave_create_view_post(init_feasible_db, client):
    """Test leave create view post."""
    client.login(username="temporary", password="temporary")
    staff_member = get_user_model().objects.first()
    data = {
        "staff_member": staff_member.id,
        "description": "Leave",
        "start_date": datetime.datetime.now(),
        "end_date": datetime.datetime.now() + datetime.timedelta(days=2),
    }
    response = client.post(reverse("leave_create"), data)
    assert response.status_code == 302
    assert reverse("leave_list") in response.url
