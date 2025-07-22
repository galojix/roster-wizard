# Pull base image
FROM python:3.13
# Compile Python files to bytecode after installation
ENV UV_COMPILE_BYTECODE=1
# Set work directory
WORKDIR /roster_app/roster_wizard
# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock /roster_app/
# Install virtual environment
RUN uv sync --locked
# Set uv cache directory for subsequent uses of uv by container user
ENV UV_CACHE_DIR=/tmp/uv_cache
# Copy project
COPY ./roster_wizard /roster_app/roster_wizard
