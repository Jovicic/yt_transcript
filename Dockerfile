FROM python:3.14-slim

ENV UV_SYSTEM_PYTHON=1

COPY --from=ghcr.io/astral-sh/uv:0.9.11 /uv /uvx /bin/

WORKDIR /app

# Define ARGs for UID and GID
ARG UID=1000
ARG GID=1000

# Create user and group
RUN groupadd -g "${GID}" appgroup && \
    useradd -u "${UID}" -g appgroup -m appuser

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

ADD . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Create data directory and set permissions
RUN mkdir -p /data && \
    chown -R appuser:appgroup /app /data

# Switch to non-root user
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
