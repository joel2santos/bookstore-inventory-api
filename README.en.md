# Bookstore Inventory API (English)

REST API for a book retail chain to manage inventory, validate prices against live exchange rates, and calculate suggested selling prices.

## Project Requirements

**Functional:**
- Manage book inventory (CRUD: create, list, retrieve, update, delete)
- Validate prices with live USD → local currency exchange rates
- Calculate suggested selling price (cost × exchange rate × 1.40 margin)
- Search books by category
- Filter books by low stock threshold

**Stack:**
- Python 3.11
- Django 5.2
- Django REST Framework
- PostgreSQL 15
- Docker & Docker Compose
- Traefik v2.11 (reverse proxy)
- gunicorn (production WSGI)

## Installation and Execution

### Prerequisites
- Docker and Docker Compose installed

### Run with Docker Compose

```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your values (see .env explanations below)
# At minimum set SECRET_KEY to a strong random value

# Build and start
docker compose up -d --build

# The API is available at http://localhost/ (via Traefik on port 80)

# Stop
docker compose down

# Stop and remove volumes
docker compose down -v
```

### Run tests

```bash
SECRET_KEY=k DEBUG=True DJANGO_SETTINGS_MODULE=config.test_settings .venv/bin/python manage.py test interface.api.books -v 2
```

## .env Explanations

| Variable | Description | Example |
|----------|-------------|---------|
| SECRET_KEY | Django cryptographic signing key. **Required** — no fallback. Generate a strong random value. | django-insecure-changeme-in-prod |
| DEBUG | Django debug mode. Defaults to False. Set True only for local development. | True |
| ALLOWED_HOSTS | Comma-separated list of allowed host/domain names. | localhost,127.0.0.1 |
| DB_NAME | PostgreSQL database name. | bookstore_inventory |
| DB_USER | PostgreSQL username. | postgres |
| DB_PASSWORD | PostgreSQL password. | postgres |
| DB_HOST | PostgreSQL host. Inside Compose, use the service name db. | db |
| DB_PORT | PostgreSQL port. | 5432 |
| EXCHANGE_RATE_API_URL | External exchange rate API endpoint. | https://api.exchangerate-api.com/v4/latest/USD |
| DEFAULT_LOCAL_CURRENCY | Default target currency for price conversion (seeds the DB fallback rate). | VES |

> .env is gitignored. Only .env.example is committed. Never commit real secrets.

## Endpoint Examples

Base URL: http://localhost/ (Traefik routes to the app internally)

### Create a book
```bash
curl -X POST http://localhost/books/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "El Quijote",
    "author": "Miguel de Cervantes",
    "isbn": "978-84-376-0494-7",
    "cost_usd": 15.99,
    "stock_quantity": 25,
    "category": "Literatura Clásica",
    "supplier_country": "ES"
  }'
# → 201 Created
```

### List books (paginated)
```bash
curl http://localhost/books/?page=1
# → 200 OK, {"count":..., "next":null, "previous":null, "results":[...]}
```

### Get book by ID
```bash
curl http://localhost/books/1/
# → 200 OK
```

### Update a book
```bash
curl -X PUT http://localhost/books/1/ \
  -H "Content-Type: application/json" \
  -d '{"title": "El Quijote (edited)", "stock_quantity": 30}'
# → 200 OK
```

### Delete a book
```bash
curl -X DELETE http://localhost/books/1/
# → 204 No Content
```

### Search by category
```bash
curl "http://localhost/books/search?category=Literatura"
# → 200 OK, paginated results matching category (icontains)
```

### Low stock filter
```bash
curl "http://localhost/books/low-stock?threshold=10"
# → 200 OK, books with stock_quantity <= 10
# Default threshold is 10 if omitted
```

### Calculate suggested selling price
```bash
curl -X POST http://localhost/books/1/calculate-price/
# → 200 OK, {"book_id":1,"cost_usd":"15.99","exchange_rate":"922.56","cost_local":"14751.73","margin_percentage":40,"selling_price_local":"20652.42","currency":"VES","calculation_timestamp":"2026-11-25T00:48:32Z"}
```

The price calculation persists selling_price_local on the book record. If the external exchange-rate API is unreachable, it falls back to the rate stored in the ExchangeRateConfig database table (seeded from DEFAULT_LOCAL_CURRENCY).

## Architecture

Clean architecture with four layers:
- domain/books/ — framework-agnostic entities and exceptions
- application/books/ — use case services and abstract interfaces
- infrastructure/db/ — Django ORM models and repository implementation
- infrastructure/external/ — external exchange-rate gateway
- interface/api/books/ — DRF serializers, views, and URLs

No authentication is configured (by design decision). Rate limiting is applied globally (anon: 100/day, user: 1000/day).
