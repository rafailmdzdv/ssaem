# syntax = docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:0.11.32-python3.13-trixie-slim AS development_build

LABEL maintainer="ssaem.rafailmdzdv.ru"
LABEL vendor="ssaem.rafailmdzdv.ru"

# `DJANGO_ENV` arg is used to make prod / dev builds:
ARG DJANGO_ENV \
  # Needed for fixing permissions of files created by Docker:
  UID=1000 \
  GID=1000

ENV DJANGO_ENV=${DJANGO_ENV} \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # uv:
  UV_CACHE_DIR='/var/cache/uv' \
  UV_PYTHON_CACHE_DIR='/var/cache/uv/python' \
  UV_PYTHON_INSTALL_DIR='/opt/uv/python' \
  UV_PROJECT_ENVIRONMENT='/opt/venv' \
  UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

# System deps (we don't use exact versions because it is hard to update them,
# pin when needed):
# hadolint ignore=DL3008
RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    bash \
    brotli \
    build-essential \
    curl \
    gettext \
    git \
    libpq-dev \
    tini \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /code

RUN groupadd -g "${GID}" -r web \
  && useradd -d '/code' -g web -l -r -u "${UID}" web \
  && chown web:web -R '/code' \
  # Static and media files:
  && mkdir -p '/var/www/django/static' '/var/www/django/media' \
  && chown web:web '/var/www/django/static' '/var/www/django/media'

# Copy only requirements, to cache them in docker layer:
COPY --chown=web:web ./uv.lock ./pyproject.toml /code/

# Project initialization:
# hadolint ignore=SC2046
RUN --mount=type=cache,target="$UV_CACHE_DIR" \
  echo "$DJANGO_ENV" \
  && uv sync \
    $(if [ "$DJANGO_ENV" = 'production' ]; then echo '--no-dev'; fi) \
    --locked --no-progress

# Activating the project's virtual environment:
ENV PATH="/opt/venv/bin:${PATH}"

# This is a special case. We need to run this script as an entry point:
COPY ./docker/django/entrypoint.sh /docker-entrypoint.sh

# Setting up proper permissions:
RUN chmod +x '/docker-entrypoint.sh' \
  # Replacing line separator CRLF with LF for Windows users:
  && sed -i 's/\r$//g' '/docker-entrypoint.sh'

# Running as non-root user:
USER web

# We customize how our app is loaded with the custom entrypoint:
ENTRYPOINT ["tini", "--", "/docker-entrypoint.sh"]


# The following stage is only for production:
FROM development_build AS production_build
COPY --chown=web:web ./src /code
# Runtime scripts, required to start the application:
COPY --chown=web:web \
  ./docker/django/gunicorn.sh \
  ./docker/django/gunicorn_config.py \
  /code/docker/django/
