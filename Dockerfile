FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System dependencies for PyMuPDF, psycopg2, and reportlab
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmupdf-dev \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
# Create necessary directories for media and static files
RUN mkdir -p /app/media/projects/full \
    && mkdir -p /app/media/projects/preview \
    && mkdir -p /app/staticfiles \
    && chmod +x /app/entrypoint.sh

# Set proper permissions
RUN chown -R root:root /app/media /app/staticfiles

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python manage.py check --database default || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
