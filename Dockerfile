FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements/prod.txt requirements/prod.txt
RUN pip install --no-cache-dir -r requirements/prod.txt

COPY . .

RUN chmod +x scripts/entrypoint.sh

# Build static files at image build time (SECRET_KEY only needed for collectstatic)
ENV SECRET_KEY=build-time-placeholder
RUN python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["scripts/entrypoint.sh"]
