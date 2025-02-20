# Use the official Docker Hub Ubuntu base image
FROM ubuntu:24.04

# Prevent needing to configure debian packages, stopping the setup of
# the docker container.
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# Install necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-poetry \
    unzip \
    wget \
    curl \
    software-properties-common \
    gnupg2 \
    cabextract \
    p7zip-full \
    && rm -rf /var/lib/apt/lists/*

# Add Wine repository and install Wine
RUN dpkg --add-architecture i386 && \
    mkdir -pm755 /etc/apt/keyrings && \
    wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key && \
    wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/noble/winehq-noble.sources && \
    apt-get update && \
    apt-get install -y --install-recommends winehq-stable && \
    rm -rf /var/lib/apt/lists/*

# Install Wine Mono
RUN wget https://github.com/wine-mono/wine-mono/releases/download/wine-mono-9.4.0/wine-mono-9.4.0-x86.msi && \
    wine msiexec /i wine-mono-9.4.0-x86.msi /quiet /qn && \
    rm wine-mono-9.4.0-x86.msi

# Download and set up RegRipper
RUN mkdir -p /opt/regripper && \
    wget -O /opt/regripper/regripper.zip https://github.com/keydet89/RegRipper3.0/archive/refs/heads/master.zip && \
    unzip /opt/regripper/regripper.zip -d /opt/regripper/ && \
    mv /opt/regripper/RegRipper3.0-master/* /opt/regripper/ && \
    rm -rf /opt/regripper/RegRipper3.0-master /opt/regripper/regripper.zip

# Set permissions for RegRipper
RUN chmod +x /opt/regripper/*

# Configure poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Configure debugging
ARG OPENRELIK_PYDEBUG
ENV OPENRELIK_PYDEBUG ${OPENRELIK_PYDEBUG:-0}
ARG OPENRELIK_PYDEBUG_PORT
ENV OPENRELIK_PYDEBUG_PORT ${OPENRELIK_PYDEBUG_PORT:-5678}

# Set working directory
WORKDIR /openrelik

# Copy poetry toml and install dependencies
COPY ./pyproject.toml ./poetry.lock .
RUN poetry install --no-interaction --no-ansi

# Copy files needed to build
COPY . ./

# Install the worker and set environment to use the correct python interpreter.
RUN poetry install && rm -rf $POETRY_CACHE_DIR
ENV VIRTUAL_ENV=/app/.venv PATH="/openrelik/.venv/bin:$PATH"

# Default command if not run from docker-compose (and command being overridden)
CMD ["celery", "--app=src.tasks", "worker", "--task-events", "--concurrency=1", "--loglevel=INFO"]
