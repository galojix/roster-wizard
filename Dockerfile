# Pull base image
FROM python:3.12
# Run as a non-privileged user
RUN useradd -ms /bin/sh -u 1000 app
USER app
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Set work directory
WORKDIR /roster_app/roster_wizard
# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock /roster_app
# Install virtual environment
RUN uv sync --locked
# Copy project
COPY --chown=app:app ./roster_wizard /roster_app/roster_wizard
