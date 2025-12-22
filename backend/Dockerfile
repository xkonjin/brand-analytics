# =============================================================================
# Brand Analytics API - Docker Image
# =============================================================================
# Multi-stage build for optimized production image
# =============================================================================

FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install system dependencies for WeasyPrint and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
# Context is from root, so we need backend/ prefix
COPY backend/requirements.txt .

# Install Python dependencies (skip playwright for now to reduce size)
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir \
    fastapi uvicorn[standard] \
    sqlalchemy aiosqlite \
    httpx beautifulsoup4 lxml \
    openai textstat \
    pydantic pydantic-settings python-dotenv \
    redis celery tenacity aiofiles

# Copy application code from backend/
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini .
COPY backend/start.sh .

# Create data directory for SQLite
RUN mkdir -p /app/data

# Make start.sh executable
RUN chmod +x start.sh

# Expose port (Railway uses dynamic port)
EXPOSE 8000

# Environment variables
ENV PORT=8000
ENV WEB_ONLY=true

# Health check (uses $PORT)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:${PORT:-8000}/health')" || exit 1

# Run the application
CMD ["./start.sh"]
