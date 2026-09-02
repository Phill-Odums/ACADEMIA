#!/usr/bin/env bash
set -e

if [ -z "${DATABASE_URL:-}" ]; then
    echo "ERROR: DATABASE_URL is not configured on this Render web service."
    echo "Link the persistent Postgres database to the service before starting the app."
    exit 1
fi

echo "Running database migrations..."
python manage.py migrate --noinput
python seed_data.py

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-2}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -