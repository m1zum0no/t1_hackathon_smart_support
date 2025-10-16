# Build stage
FROM python:3.11.3-slim AS builder

ENV \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.5.1

WORKDIR /opt/chat

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install "poetry==$POETRY_VERSION" && \
    poetry config virtualenvs.create false

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-root --no-dev && \
    apt-get purge -y --auto-remove build-essential && \
    rm -rf /var/lib/apt/lists/*

# Runtime stage
FROM python:3.11.3-slim

ENV \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

EXPOSE 8001

WORKDIR /opt/chat

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Make entrypoint script executable
RUN chmod +x /opt/chat/docker-entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/bin/bash", "/opt/chat/docker-entrypoint.sh"]