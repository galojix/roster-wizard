"""View Testing."""

import pytest
import datetime

from django.urls import reverse
from django.test import SimpleTestCase
from django.contrib.auth import get_user_model

from rosters.models import Day, Role, ShiftRule, ShiftSequence, Shift, DayGroup
from rosters.views import generate_roster, AsyncResult
from rosters.logic import SolutionNotFeasible

pytestmark = pytest.mark.django_db


def test_day_detail_view(init_feasible_db, client):
    """Test day detail view."""
    client.login(username="temporary", password="temporary")
    day = Day.objects.get(number=1)
    response = client.get(reverse("day_detail", kwargs={"pk": day.id}))
    assert response.status_code == 200
    assert "Day: 1" in response.rendered_content
    assert "day_detail.html" in [t.name for t in response.templates]


def test_roster_by_staff_view(init_db, client):
    """Test roster by staff view."""
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("roster_by_staff"))
    assert response.status_code == 200
    assert "Roster By Staff:" in response.rendered_content
    assert "roster_by_staff.html" in [t.name for t in response.templates]


def test_roster_by_staff_view_start_date(init_roster_db, client):
    """Test roster by staff view."""
    client.login(username="temporary", password="temporary")
    session = client.session
    session["start_date"] = datetime.datetime.now().date().strftime("%d-%b-%Y")
    session.save()
    response = client.get(reverse("roster_by_staff"))
    assert response.status_code == 200
    assert "Roster By Staff:" in response.rendered_content
    assert "roster_by_staff.html" in [t.name for t in response.templates]


def test_roster_by_day_view(init_db, client):
    """Test roster by day view."""
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("timeslot_list"))
    assert response.status_code == 200
    assert "Roster By Day:" in response.rendered_content
    assert "timeslot_list.html" in [t.name for t in response.templates]


def test_roster_by_day_view_start_date(init_db, client):
    """Test roster by day view."""
    client.login(username="temporary", password="temporary")
    session = client.session
    session["start_date"] = "22-MAR-2010"
    session.save()
    response = client.get(reverse("timeslot_list"))
    assert response.status_code == 200
    assert "Roster By Day:" in response.rendered_content
    assert "timeslot_list.html" in [t.name for t in response.templates]


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


def test_leave_list_view_start_date(init_feasible_db, client, mocker):
    """Test leave list view."""
    client.login(username="temporary", password="temporary")
    session = client.session
    session["start_date"] = "22-MAR-2010"
    session.save()
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
    mocker.patch.object(AsyncResult, "get", return_value="Roster is complete...")
    response = client.get(reverse("roster_generation_status", args=("12345",)))
    assert response.status_code == 200
    assert "Roster is complete..." in str(response.getvalue())
    assert "roster_generation_status.html" in [t.name for t in response.templates]


def test_roster_generation_status_view_infeasible(init_db, client, mocker):
    """Test roster generation status view."""
    client.login(username="temporary", password="temporary")
    mocker.patch.object(AsyncResult, "ready", return_value=True)
    mocker.patch.object(AsyncResult, "get", side_effect=SolutionNotFeasible)
    response = client.get(reverse("roster_generation_status", args=("12345",)))
    assert response.status_code == 200
    assert (
        "Could not generate roster, ensure staff details and rules are correct..."
        in str(response.getvalue())
    )
    assert "roster_generation_status.html" in [t.name for t in response.templates]


def test_roster_generation_status_view_too_many_staff(init_db, client, mocker):
    """Test roster generation status view."""
    client.login(username="temporary", password="temporary")
    mocker.patch.object(AsyncResult, "ready", return_value=True)
    mocker.patch.object(AsyncResult, "get", side_effect=SolutionNotFeasible)
    response = client.get(reverse("roster_generation_status", args=("12345",)))
    assert response.status_code == 200
    assert (
        "Could not generate roster, ensure staff details and rules are correct..."
        in str(response.getvalue())
    )
    assert "roster_generation_status.html" in [t.name for t in response.templates]


def test_roster_generation_status_view_processing(init_db, client, mocker):
    """Test roster generation status view."""
    client.login(username="temporary", password="temporary")
    mocker.patch.object(AsyncResult, "ready", return_value=False)
    response = client.get(reverse("roster_generation_status", args=("12345",)))
    assert response.status_code == 200
    assert "Processing..." in str(response.getvalue())
    assert "roster_generation_status.html" in [t.name for t in response.templates]


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


def test_staff_request_update_view(init_feasible_db, client):
    """Test leave create view post."""
    client.login(username="temporary", password="temporary")
    staff_member = get_user_model().objects.first()
    response = client.get(reverse("staffrequest_update", args=(staff_member.id,)))
    assert response.status_code == 200
    assert "staffrequest_update.html" in [t.name for t in response.templates]


def test_staff_request_update_view_start_date(init_feasible_db, client):
    """Test leave create view post."""
    client.login(username="temporary", password="temporary")
    session = client.session
    session["start_date"] = datetime.datetime.now().date().strftime("%d-%b-%Y")
    session.save()
    staff_member = get_user_model().objects.first()
    response = client.get(reverse("staffrequest_update", args=(staff_member.id,)))
    assert response.status_code == 200
    assert "staffrequest_update.html" in [t.name for t in response.templates]


def test_staff_request_update_view_post(init_feasible_db, client):
    """Test leave create view post."""
    client.login(username="temporary", password="temporary")
    staff_member = get_user_model().objects.get(username="one")
    data = {
        "request_1": "Yes",
        "priority_1": 10,
        "request_2": "No",
        "priority_2": 10,
    }
    response = client.post(
        reverse("staffrequest_update", args=(staff_member.id,)), data
    )
    assert response.status_code == 302
    assert reverse("staffrequest_list") in response.url


def test_download_csv(init_feasible_db, client):
    """Test download CSV."""
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("download_csv"))
    assert response.status_code == 200
    assert "Staff Member" in str(response.content)


def test_download_csv_start_date(init_feasible_db, client):
    """Test download CSV."""
    client.login(username="temporary", password="temporary")
    session = client.session
    session["start_date"] = datetime.datetime.now().date().strftime("%d-%b-%Y")
    session.save()
    response = client.get(reverse("download_csv"))
    assert response.status_code == 200
    assert "Staff Member" in str(response.content)


def test_shift_rule_role_create_view_post(init_feasible_db, client):
    """Test shift rule role create view post."""
    client.login(username="temporary", password="temporary")
    shiftrule = ShiftRule.objects.first()
    role = Role.objects.first()
    data = {
        "role": role.id,
        "count": 2,
    }
    response = client.post(reverse("shiftrulerole_create", args=(shiftrule.id,)), data)
    assert response.status_code == 302
    assert reverse("shiftrule_list") in response.url


def test_staff_rule_shift_create_view_post(init_feasible_db, client):
    """Test staff rule shift create view post."""
    client.login(username="temporary", password="temporary")
    staffrule = ShiftSequence.objects.first()
    shift = Shift.objects.first()
    data = {
        "shift": shift.id,
        "position": 2,
    }
    response = client.post(reverse("staffruleshift_create", args=(staffrule.id,)), data)
    assert response.status_code == 302
    assert reverse("staffrule_list") in response.url


def test_day_group_create_view_post(init_feasible_db, client):
    """Test day group create view post."""
    client.login(username="temporary", password="temporary")
    data = {
        "name": "NewGroup",
    }
    response = client.post(reverse("daygroup_create"), data)
    assert response.status_code == 302
    assert reverse("daygroup_list") in response.url


def test_day_group_day_create_view_post(init_feasible_db, client):
    """Test day group day create view post."""
    client.login(username="temporary", password="temporary")
    daygroup = DayGroup.objects.create(name="Test")
    day = Day.objects.last()
    data = {
        "day": day.id,
    }
    response = client.post(reverse("daygroupday_create", args=(daygroup.id,)), data)
    assert response.status_code == 302
    assert "/rosters/daygroupday" in response.url


def test_day_group_day_create_view_post_invalid(init_feasible_db, client):
    """Test day group day create view post with invalid data."""
    client.login(username="temporary", password="temporary")
    daygroup = DayGroup.objects.first()
    day = Day.objects.last()
    data = {
        "day": day.id,
    }
    response = client.post(reverse("daygroupday_create", args=(daygroup.id,)), data)
    assert response.status_code == 200
    assert "is already in the Day Group" in response.rendered_content
    assert "daygroupday_create.html" in [t.name for t in response.templates]


def test_day_set_create_view_post(init_feasible_db, client):
    """Test day group create view post."""
    client.login(username="temporary", password="temporary")
    data = {
        "number_of_days": 10,
    }
    response = client.post(reverse("day_set_create"), data)
    assert response.status_code == 302
    assert "/rosters/day/" in response.url


def test_staff_request_list_view(init_feasible_db, client):
    """Test staff request list view."""
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("staffrequest_list"))
    assert response.status_code == 200
    assert "Staff Requests:" in response.rendered_content
    assert "staffrequest_list.html" in [t.name for t in response.templates]


def test_staff_request_list_view_start_date(init_feasible_db, client):
    """Test staff request list view."""
    client.login(username="temporary", password="temporary")
    session = client.session
    session["start_date"] = datetime.datetime.now().date().strftime("%d-%b-%Y")
    session.save()
    response = client.get(reverse("staffrequest_list"))
    assert response.status_code == 200
    assert "Staff Requests:" in response.rendered_content
    assert "staffrequest_list.html" in [t.name for t in response.templates]


def test_role_list_view(init_feasible_db, client):
    """Test role list view."""
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("role_list"))
    assert response.status_code == 200
    assert "Staff by Role:" in response.rendered_content
    assert "role_list.html" in [t.name for t in response.templates]


def test_shift_rule_list_view(init_feasible_db, client):
    """Test shift rule list view."""
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("shiftrule_list"))
    assert response.status_code == 200
    assert "Skill Mix Rules:" in response.rendered_content
    assert "shiftrule_list.html" in [t.name for t in response.templates]


def test_shift_rule_role_list_view(init_feasible_db, client):
    """Test shift rule role list view."""
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("shiftrulerole_list"))
    assert response.status_code == 200
    assert "Shift Rule Roles:" in response.rendered_content
    assert "shiftrulerole_list.html" in [t.name for t in response.templates]


def test_staff_rule_list_view(init_feasible_db, client):
    """Test staff rule list view."""
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("staffrule_list"))
    assert response.status_code == 200
    assert "Shift Sequences:" in response.rendered_content
    assert "staffrule_list.html" in [t.name for t in response.templates]


def test_day_group_list_view(init_feasible_db, client):
    """Test day group list view."""
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("daygroup_list"))
    assert response.status_code == 200
    assert "Day Groups:" in response.rendered_content
    assert "daygroup_list.html" in [t.name for t in response.templates]


def test_day_list_view(init_feasible_db, client):
    """Test day list view."""
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("day_list"))
    assert response.status_code == 200
    assert "Days:" in response.rendered_content
    assert "day_list.html" in [t.name for t in response.templates]


def test_select_roster_period_view_post(init_roster_db, client):
    """Test roster by staff view."""
    client.login(username="temporary", password="temporary")
    data = {
        "start_date": datetime.datetime.now().date(),
    }
    response = client.post(reverse("select_roster_period"), data)
    assert response.status_code == 302
    assert reverse("home") in response.url


def test_custom_user_list_view(init_feasible_db, client):
    """Test custom user list view."""
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("customuser_list"))
    assert response.status_code == 200
    assert "Staff:" in response.rendered_content
    assert "customuser_list.html" in [t.name for t in response.templates]
