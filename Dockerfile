FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# Install PostgreSQL build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy ALL requirement files because prod.txt includes base.txt
COPY requirements/ requirements/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements/prod.txt

# Copy the complete Django project
COPY . .

# Make entrypoint executable
RUN chmod +x scripts/entrypoint.sh

# Collect static files
# A temporary key is sufficient during Docker build
ENV SECRET_KEY=build-time-placeholder

RUN python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["scripts/entrypoint.sh"]