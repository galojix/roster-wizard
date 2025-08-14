"""Celery tasks."""

from datetime import datetime
from dateutil import parser

from celery import shared_task
from .logic import RosterGenerator


@shared_task()
def generate_roster(start_date):
    """Generate roster."""
    if not isinstance(start_date, datetime):
        start_date = parser.isoparse(start_date)

    with RosterGenerator(start_date, max_concurrent=1) as roster:
        roster.create()

    return "Roster is complete..."
