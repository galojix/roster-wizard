import pytest

from django.urls import reverse
from django.contrib.auth import get_user_model

from rosters.models import Day

# pytestmark = pytest.mark.django_db


@pytest.fixture()
@pytest.mark.django_db
def init_db():
    get_user_model().objects.create_user(
        username="temporary",
        password="temporary",
        available=True,
        shifts_per_roster=10,
    )


@pytest.mark.django_db
def test_day_detail_view(init_db, client):
    day = Day.objects.create(number=5)
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("day_detail", kwargs={"pk": day.id}))
    assert response.status_code == 200
    assert "Day: 5" in response.rendered_content
    assert "day_detail.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_roster_list_view(init_db, client):
    client.login(username="temporary", password="temporary")
    response = client.get(reverse("roster_list"))
    assert response.status_code == 200
    assert "Roster:" in response.rendered_content
    assert "roster_list.html" in [t.name for t in response.templates]
