#!/usr/bin/env bash
set -e

if [ -z "${DATABASE_URL:-}" ]; then
    echo "ERROR: DATABASE_URL is not configured on this Render web service."
    echo "Link the persistent Postgres database to the service before starting the app."
    exit 1
fi

echo "Running database migrations..."
python manage.py migrate --noinput

if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    echo "Ensuring configured Django superuser exists..."
    DJANGO_SUPERUSER_USERNAME="$DJANGO_SUPERUSER_USERNAME" \
    DJANGO_SUPERUSER_EMAIL="$DJANGO_SUPERUSER_EMAIL" \
    DJANGO_SUPERUSER_PASSWORD="$DJANGO_SUPERUSER_PASSWORD" \
    python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ['DJANGO_SUPERUSER_USERNAME']
email = os.environ['DJANGO_SUPERUSER_EMAIL']
password = os.environ['DJANGO_SUPERUSER_PASSWORD']

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        'email': email,
        'is_staff': True,
        'is_superuser': True,
        'role': User.Role.SUPERADMIN,
    },
)
if created:
    user.set_password(password)
    user.save(update_fields=['password', 'is_staff', 'is_superuser', 'role'])
    print(f'Created superuser: {username}')
else:
    print(f'Superuser already exists; leaving it unchanged: {username}')
PY
else
    echo "No DJANGO_SUPERUSER_* variables configured; skipping superuser bootstrap."
fi

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