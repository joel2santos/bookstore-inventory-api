# Project Scope

## Business context

A bookstore inventory API that tracks books, their cost in USD, stock levels, and category.
Core capabilities:

- Maintain books (create, list, retrieve, update, delete).
- Search books by category.
- List low-stock books (below a threshold).
- Calculate and persist a suggested local selling price: `cost_local = cost_usd × exchange_rate`, then `selling_price_local = cost_local × 1.40` (40% margin).
- Exchange rate is fetched from a live JSON API, with a database-stored fallback rate so the business can update it without redeploying.

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Web framework | Django 5.2 |
| API framework | Django REST Framework |
| Database | PostgreSQL 15 |
| Container orchestration | Docker Compose |
| Reverse proxy / ingress | Traefik v2.11 |
| WSGI server | gunicorn |
| DB driver | psycopg2-binary |
| HTTP client | requests |

## Architecture

Clean architecture with four layers:

- **`domain/`** — plain Python entities (`Book`) and exceptions (`BookNotFound`, `ExchangeRateUnavailable`, etc.). No framework dependencies.
- **`application/`** — use-case services (`CalculateSellingPrice`) and abstract repository/gateway interfaces (`AbstractBookRepository`, `AbstractExchangeRateGateway`).
- **`infrastructure/`** — Django ORM models and repository (`DjangoBookRepository`), external gateway (`ExchangeRateGateway`) calling the exchange-rate API with a DB fallback.
- **`interface/api/`** — DRF `BookViewSet`, serializers, and URL routing.

Dependencies point inward: interface and infrastructure depend on application and domain, never the reverse.

## Business rules

- `cost_usd` must be strictly positive (> 0).
- `stock_quantity` must be non-negative (>= 0).
- ISBN must be a valid ISBN-10 or ISBN-13 (check digit verified; hyphens and spaces allowed) and is unique across books.
- Suggested margin is 40% over the local cost.
- Default local currency is VES (Venezuelan bolívar), overridable via `DEFAULT_LOCAL_CURRENCY`.
- Exchange rate: live API first, then `ExchangeRateConfig` singleton row in the database as fallback.

## Out of scope

- Authentication / authorization (none, by user decision) — all endpoints are open.
- Frontend or admin UI for end users.
- Production WSGI stack beyond gunicorn.
- Observability (metrics, tracing, logging infrastructure).
