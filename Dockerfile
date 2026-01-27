FROM python:3.12-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies only (not the package itself)
RUN pip install --no-cache-dir \
    "mcp>=1.3.0" \
    "fastmcp>=2.0.0" \
    "curl_cffi>=0.7.0" \
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

# Copy database build script
COPY scripts/build_database.py /app/scripts/

# Add src to Python path
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV HTTP_PORT=8080
ENV RATE_LIMIT_REQUESTS=100

EXPOSE 8080

# 30s start period for DB build on first startup (~7s)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "jlcpcb_mcp.server"]
