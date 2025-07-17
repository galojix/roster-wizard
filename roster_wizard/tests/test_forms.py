"""Form Testing."""

import datetime

# import pytest

from rosters.forms import GenerateRosterForm

# pytestmark = pytest.mark.django_db


def test_generate_roster_form(mocker):
    """Test generate roster form."""
    request = mocker.Mock()
    request.session = {"start_date": "22-MAR-2010"}
    form = GenerateRosterForm(request, data={"start_date": datetime.datetime.now()})
    assert form.is_valid()
