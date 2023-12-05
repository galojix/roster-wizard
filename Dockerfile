# Pull base image
FROM python:3.11
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Set work directory
WORKDIR /roster
# Install dependencies
COPY Pipfile Pipfile.lock /roster/
RUN python -m pip install --upgrade pip && \
    python -m pip install pipenv && \
    pipenv requirements --dev > requirements.txt && \
    pip uninstall --yes pipenv && \
    pip install -r requirements.txt
# Copy project
COPY . /roster/
