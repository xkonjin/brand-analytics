# =============================================================================
# Dockerfile for Brand Analytics Backend
# =============================================================================
# Multi-stage build for optimized production image
# Includes Playwright for web scraping capabilities
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Base Python image with dependencies
# ---------------------------------------------------------------------------
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for:
# - PostgreSQL (libpq-dev)
# - WeasyPrint PDF generation (libpango, libcairo, etc.)
# - Playwright browsers
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    build-essential \
    # PostgreSQL client
    libpq-dev \
    # WeasyPrint dependencies
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    # Playwright dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    # Utilities
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# ---------------------------------------------------------------------------
# Stage 2: Install Python dependencies
# ---------------------------------------------------------------------------
FROM base as dependencies

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install Playwright browsers (Chromium only for smaller image)
RUN playwright install chromium && \
    playwright install-deps chromium

# ---------------------------------------------------------------------------
# Stage 3: Production image
# ---------------------------------------------------------------------------
FROM dependencies as production

# Copy application code
COPY app /app/app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default command: Run FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ---------------------------------------------------------------------------
# Stage 4: Development image (with hot reload)
# ---------------------------------------------------------------------------
FROM dependencies as development

# Copy application code
COPY app /app/app

# Install development dependencies
RUN pip install pytest pytest-asyncio pytest-cov black ruff mypy

# Expose port
EXPOSE 8000

# Development command with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

