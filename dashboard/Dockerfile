FROM python:3.12-slim

# uv installs the exact versions in uv.lock (mounted for that step only); the image never runs pip.
ENV UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app
# /app/data is the SQLite store; compose mounts a named volume there, which copies this owner.
RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/data \
    && chown appuser:appuser /app/data

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN --mount=from=ghcr.io/astral-sh/uv:0.12.24,source=/uv,target=/bin/uv \
    uv sync --frozen --no-dev --no-editable

USER appuser
# Binding beyond loopback makes the server refuse to start without DASHBOARD_PASSWORD.
ENV DASHBOARD_HOST=0.0.0.0 \
    DASHBOARD_PORT=8050
EXPOSE 8050
HEALTHCHECK --interval=60s --timeout=5s --start-period=10s \
    CMD ["python", "-c", "import sys, http.client; c = http.client.HTTPConnection('127.0.0.1', 8050, timeout=4); c.request('GET', '/healthz'); sys.exit(c.getresponse().status != 200)"]
CMD ["/app/.venv/bin/pcbparts-dashboard", "serve"]
