FROM python:3.10-slim

ARG dev

ENV YOUR_ENV=${YOUR_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.4.2

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$YOUR_ENV" == production && echo "--no-dev") \
  --no-interaction --no-ansi

# copy codes
COPY . /app/

# RUN mkdir /app
# WORKDIR /app
# RUN python3 -m venv venv
# RUN . ./venv/bin/activate
# RUN python3 -m pip install poetry
# COPY poetry.lock /
# COPY pyproject.toml /
# RUN --mount=type=cache,target=/app/.cache/pypoetry/cache \
#     --mount=type=cache,target=/app/.cache/pypoetry/artifacts \
#     poetry install --compile

# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

