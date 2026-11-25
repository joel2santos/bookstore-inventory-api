FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    django==5.2.13 \
    psycopg2-binary \
    requests \
    djangorestframework \
    gunicorn

COPY . /app

EXPOSE 8000

CMD python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
