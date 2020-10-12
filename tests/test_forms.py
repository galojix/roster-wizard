"""Form Testing."""
import datetime
import pytest
from unittest.mock import Mock

from rosters.forms import GenerateRosterForm

pytestmark = pytest.mark.django_db


def test_generate_roster_form(init_feasible_db, client):
    """Test generate roster form."""
    client.login(username="temporary", password="temporary")
    request = Mock()
    request.session = {"start_date": "22-MAR-2010"}
    form = GenerateRosterForm(
        request, data={"start_date": datetime.datetime.now()}
    )
    assert form.is_valid()
