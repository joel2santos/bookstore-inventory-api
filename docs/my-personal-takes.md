## What I would change

**#1 — Cache prices in Redis instead of persisting in DB**
`selling_price_local` is currently written to the `Book` row. Given Venezuela's volatile economy, prices go stale quickly. A Redis cache with a 24-hour TTL would reflect rate changes faster and avoid rewriting book rows on every calculation.

**#2 — Use Go instead of Django**
Go's concurrency model fits API request handling better than Django's request/response cycle.

**#3 — Observability and customer data**
Implement a PLG (Prometheus, Loki, Grafana) stack for observability, and a Jitsu-like tool for customer data collection. Neither exists in the project today (observability is out of scope).

**#4 — Other observations**

- I would recommend using UUIDs for book identifiers instead of integers, as UUIDs are harder to guess and provide an additional level of security.
- gunicorn is used over Django's `runserver` for serving (3 workers, 120s timeout).
- `Decimal` is used for money (`cost_usd`, `selling_price_local`, exchange rate math) rather than float, avoiding floating-point rounding errors.
