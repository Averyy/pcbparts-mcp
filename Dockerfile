FROM python:3.12-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies only (not the package itself).
# Pinned exact so a rebuild (this layer is GHA-cached; a cache miss re-resolves) can't pull a new
# fastmcp/wafer/starlette that silently changes behavior. Keep in sync with pyproject.toml.
RUN pip install --no-cache-dir \
    "mcp==1.25.0" \
    "fastmcp==3.4.3" \
    "wafer-py==0.4.6" \
    "wreq==0.12.3" \
    "httpx==0.28.1" \
    "uvicorn[standard]==0.40.0" \
    "starlette==1.3.1" \
    "pydantic==2.12.5" \
    "pyyaml==6.0.3"

# Non-root runtime user, created before anything is put in /app so every file gets its owner in the
# layer that creates it. Never `chown -R /app` after the DB builds: that rewrites every file into a
# new layer and stored the ~1.1 GB of DBs twice. /app holds only these empty dirs at this point.
# /app/data must stay writable by appuser: SQLite creates -wal/-shm files next to each DB on open.
# /app/cache: docker-compose mounts a named volume here, and a new volume copies this dir's owner.
RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/data/history /app/data/wafer/cookies /app/cache \
    && chown -R appuser:appuser /app

# Copy application code (preserve src/ structure for path resolution)
COPY --chown=appuser:appuser src/ /app/src/

# Copy pyproject.toml for version info
COPY --chown=appuser:appuser pyproject.toml /app/

# Copy scraped component data
COPY --chown=appuser:appuser data/categories/ /app/data/categories/
COPY --chown=appuser:appuser data/manifest.json /app/data/
COPY --chown=appuser:appuser data/subcategories.json /app/data/

# Copy database build script and parsers module
COPY --chown=appuser:appuser scripts/build_database.py /app/scripts/

# Build the SQLite databases at image build time. The EasyEDA footprint seed CSV (built by
# scripts/build_easyeda_seed.py) is mounted for this step only: it's loaded into components.db,
# so the 40 MB CSV doesn't need to ship in the image. --mount needs BuildKit (the default builder
# since Docker 23, and what Compose v2 and buildx use).
# The builds run as root because a bind mount keeps the checkout's file mode (a umask 027/077
# checkout makes the seed unreadable to appuser); each RUN hands its DB to appuser itself, which
# costs nothing because the file is new in that layer. -B: no root-owned .pyc in /app/src.
RUN --mount=type=bind,source=data/easyeda/footprints.csv,target=/app/data/easyeda/footprints.csv \
    python -B scripts/build_database.py --data-dir /app/data --output /app/data/components.db \
    && chown appuser:appuser /app/data/components.db

# Build stock history database (data/history/ kept by .gitkeep; populated by daily scraper)
COPY --chown=appuser:appuser data/history/ /app/data/history/
COPY --chown=appuser:appuser scripts/build_history_db.py /app/scripts/
RUN python scripts/build_history_db.py --data-dir /app/data --output /app/data/stock_history.db \
    && chown appuser:appuser /app/data/stock_history.db

# Build sensor database from scraped sensor JSON data
COPY --chown=appuser:appuser data/sensors/ /app/data/sensors/
COPY --chown=appuser:appuser scripts/build_sensor_db.py /app/scripts/
RUN python scripts/build_sensor_db.py --data-dir /app/data --output /app/data/sensor.db --quiet \
    && chown appuser:appuser /app/data/sensor.db

# Build boards database from parsed OSHW YAML schematics
COPY --chown=appuser:appuser data/boards/ /app/data/boards/
COPY --chown=appuser:appuser scripts/build_boards_db.py /app/scripts/
RUN python scripts/build_boards_db.py --data-dir /app/data --output /app/data/boards.db --quiet \
    && chown appuser:appuser /app/data/boards.db

# Copy design rules (served markdown only, not raw sources)
COPY --chown=appuser:appuser data/design-rules/rules/ /app/data/design-rules/rules/

# Add src to Python path
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV HTTP_PORT=8080
ENV RATE_LIMIT_REQUESTS=100

# EasyEDA footprint answers and Mouser/DigiKey daily request counts that survive restarts (dir
# created and owned by appuser above).
ENV EASYEDA_STORE_PATH=/app/cache/easyeda.db
ENV DISTRIBUTOR_QUOTA_PATH=/app/cache/distributor_quota.json

# Run as non-root user
USER appuser

EXPOSE 8080

# 30s start period for server initialization
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "pcbparts_mcp.server"]
