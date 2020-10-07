"""Business logic testing."""

import pytest
import datetime

from rosters.logic import (
    RosterGenerator,
    SolutionNotFeasible,
    TooManyStaff,
)

pytestmark = pytest.mark.django_db


def test_feasible_roster_generation(init_feasible_db):
    """Test feasible roster generation."""
    roster = RosterGenerator(start_date=datetime.datetime.now())
    roster.create()
    assert roster.complete


def test_infeasible_roster_generation(init_infeasible_db):
    """Test infeasible roster generation."""
    roster = RosterGenerator(start_date=datetime.datetime.now())
    with pytest.raises(SolutionNotFeasible):
        roster.create()


def test_too_many_staff_roster_generation(init_too_many_staff_db):
    """Test too many staff roster generation."""
    roster = RosterGenerator(start_date=datetime.datetime.now())
    with pytest.raises(TooManyStaff):
        roster.create()
