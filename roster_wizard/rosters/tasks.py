"""Celery tasks."""

from datetime import datetime

from celery import shared_task
from dateutil import parser

from .logic import RosterGenerator


@shared_task()
def generate_roster(start_date):
    """Generate roster."""
    if not isinstance(start_date, datetime):
        start_date = parser.isoparse(start_date)

    with RosterGenerator(start_date, max_concurrent=1) as roster:
        roster.create()

    return "Roster is complete..."
