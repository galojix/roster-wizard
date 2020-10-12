"""Business logic testing."""

import pytest
import datetime

from rosters.logic import (
    RosterGenerator,
    SolutionNotFeasible,
    TooManyStaff,
)
from rosters.tasks import generate_roster

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


def test_celery_feasible_roster_generation_sync(init_feasible_db):
    """Test feasible roster generation with celery but synchronous."""
    task = generate_roster.apply(
        kwargs={"start_date": datetime.datetime.now().isoformat()}
    )
    result = task.get()
    assert result == "Roster is complete..."


def test_celery_feasible_roster_generation_task_only(init_feasible_db):
    """Test feasible roster generation task without celery."""
    result = generate_roster(start_date=datetime.datetime.now().isoformat())
    assert result == "Roster is complete..."


def test_celery_infeasible_roster_generation_sync(init_infeasible_db):
    """Test infeasible roster generation with celery but synchonous."""
    task = generate_roster.apply(
        kwargs={"start_date": datetime.datetime.now().isoformat()}
    )
    with pytest.raises(SolutionNotFeasible):
        task.get()
