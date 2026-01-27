FROM python:3.12-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Copy scraped component data (15MB compressed JSONL)
# The SQLite database will be built on first startup (~6 seconds)
COPY data/categories/ data/categories/
COPY data/manifest.json data/
COPY data/subcategories.json data/

# Copy database build script
COPY scripts/build_database.py scripts/

# Install dependencies
RUN pip install --no-cache-dir .

# Environment
ENV PYTHONUNBUFFERED=1
ENV HTTP_PORT=8080
ENV RATE_LIMIT_REQUESTS=100

EXPOSE 8080

# 30s start period for DB build on first startup (~7s)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "jlcpcb_mcp.server"]
