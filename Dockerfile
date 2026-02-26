FROM python:3.12-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies only (not the package itself)
RUN pip install --no-cache-dir \
    "mcp>=1.3.0" \
    "fastmcp>=3.0.0" \
    "wafer-py>=0.1.2" \
    "httpx>=0.27.0" \
    "uvicorn[standard]" \
    "starlette" \
    "pydantic>=2.0"

# Copy application code (preserve src/ structure for path resolution)
COPY src/ /app/src/

# Copy pyproject.toml for version info
COPY pyproject.toml /app/

# Copy scraped component data
COPY data/categories/ /app/data/categories/
COPY data/manifest.json /app/data/
COPY data/subcategories.json /app/data/

# Copy database build script and parsers module
COPY scripts/build_database.py /app/scripts/

# Build the SQLite databases at image build time
RUN python scripts/build_database.py --data-dir /app/data --output /app/data/components.db

# Build stock history database (data/history/ kept by .gitkeep; populated by daily scraper)
RUN mkdir -p /app/data/history
COPY data/history/ /app/data/history/
COPY scripts/build_history_db.py /app/scripts/
RUN python scripts/build_history_db.py --data-dir /app/data --output /app/data/stock_history.db

# Add src to Python path
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV HTTP_PORT=8080
ENV RATE_LIMIT_REQUESTS=100

# Create wafer cookie cache dir (writable at runtime)
RUN mkdir -p /app/data/wafer/cookies

# Run as non-root user
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# 30s start period for server initialization
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "pcbparts_mcp.server"]
