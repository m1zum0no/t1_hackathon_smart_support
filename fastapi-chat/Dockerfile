FROM python:3.11.3-slim

RUN apt-get update && apt-get -y upgrade

ENV \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

ENV \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.5.1

EXPOSE 8001

WORKDIR /opt/chat

COPY poetry.lock pyproject.toml ./
RUN pip install "poetry==$POETRY_VERSION"
# Export dependencies and debug
RUN poetry export --with main,test,lint --output requirements.txt
# Output requirements.txt for debugging
RUN cat requirements.txt
# Install dependencies
RUN pip install -r requirements.txt
# Explicitly install uvicorn to ensure it’s present
RUN pip install uvicorn==0.23.2

COPY . .