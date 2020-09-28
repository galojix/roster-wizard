import pytest


@pytest.fixture(scope="session")
def celery_config():
    """Celery config."""
    return {"broker_url": "amqp://", "result_backend": "rpc://"}
