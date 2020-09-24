"""Celery tasks."""
from dateutil import parser
from celery import shared_task
from .logic import RosterGenerator


@shared_task
def generate_roster(start_date):
    """Generate roster."""
    start_date = parser.isoparse(start_date)
    roster = RosterGenerator(start_date=start_date)
    roster.create()
    print("Hi!!!")
    return "Task finished"
