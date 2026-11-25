# Error Codes

All error responses are JSON: `{ "detail": "<message>" }`.

## 400 Bad Request

Input validation failure. The request was not processed.

Possible causes and messages:

| Cause | Example message |
|---|---|
| `cost_usd` is zero or negative | `cost_usd must be greater than 0` |
| `stock_quantity` is negative | `stock_quantity must be greater than or equal to 0` |
| ISBN is not a valid ISBN-10 or ISBN-13 (check digit fails) | `Invalid ISBN` / `Invalid ISBN-10 check digit` / `Invalid ISBN-13 check digit` |
| ISBN already exists (unique constraint) | `book with this isbn already exists.` |
| Required field missing or blank (e.g. `category`) | `<field>: This field is required.` / `This field may not be blank.` |
| `category` query parameter missing on `/books/search/` | `category query parameter is required` |

Applies to: `POST /books/`, `PUT /books/{id}/`, `GET /books/search/`.

## 404 Not Found

No book exists with the requested `id`.

Example message: `Book not found`.

Applies to: `GET /books/{id}/`, `PUT /books/{id}/`, `DELETE /books/{id}/`, `POST /books/{id}/calculate-price/`.

## 429 Too Many Requests

Rate limit exceeded (DRF throttling, configured in `config.settings`):

| Client class | Limit |
|---|---|
| Anonymous | 100 requests/day |
| Authenticated user | 1000 requests/day |

No authentication is implemented in this project, so requests are effectively limited by client identity as DRF resolves it.

Applies to: all endpoints.

## 500 Internal Server Error

Server-side failure.

Specific cause handled by this project:

| Cause | Message |
|---|---|
| Exchange rate unavailable | `Exchange rate unavailable` |

The calculate-price endpoint fetches a live rate from `EXCHANGE_RATE_API_URL` and falls back to the `ExchangeRateConfig` row in the database. If the live API is unreachable **and** no fallback rate is configured in the database, the request fails with `500`.

Applies to: `POST /books/{id}/calculate-price/`.
