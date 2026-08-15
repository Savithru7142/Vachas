#!/bin/bash
set -e

echo "==> Waiting for database..."
python << 'EOF'
import os, sys, time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
import django
django.setup()
from django.db import connection
for i in range(30):
    try:
        connection.ensure_connection()
        print("Database is ready.")
        break
    except Exception:
        time.sleep(2)
else:
    sys.exit("Database not available after 60 seconds.")
EOF

echo "==> Running migrations..."
python manage.py migrate --noinput

if [ "${RUN_SEED:-false}" = "true" ]; then
    echo "==> Seeding initial data..."
    python manage.py seed_vachas
fi

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-3} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
