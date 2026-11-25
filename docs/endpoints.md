# API Endpoints

Base URL: `http://localhost/` (via Traefik on port 80) or `http://localhost:8000/` (app directly).
All paths are relative to the API root. `id` is the book's database primary key (integer).

## Book resource (JSON)

```json
{
  "id": 1,
  "title": "Cien años de soledad",
  "author": "Gabriel García Márquez",
  "category": "Literatura",
  "isbn": "978-84-376-0494-7",
  "supplier_country": "VE",
  "cost_usd": "25.00",
  "selling_price_local": null,
  "stock_quantity": 50,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

| Field | Type | Notes |
|---|---|---|
| id | integer | Read-only, assigned on creation |
| title | string | Required |
| author | string | Required |
| category | string | Required |
| isbn | string | Required, ISBN-10 or ISBN-13 (hyphens/spaces allowed), unique |
| supplier_country | string | Required, 2-character country code |
| cost_usd | string (decimal) | Required, must be > 0 |
| selling_price_local | string or null | Read-only, set by calculate-price |
| stock_quantity | integer | Required, must be >= 0 |
| created_at | datetime | Read-only |
| updated_at | datetime | Read-only |

Paginated list responses use:

```json
{
  "count": 12,
  "next": "http://localhost/books/?page=2",
  "previous": null,
  "results": [ { ...book... } ]
}
```

Error responses use `{ "detail": "<message>" }`.

---

## POST /books/

Create a new book.

**Request body (JSON):**

```json
{
  "title": "Cien años de soledad",
  "author": "Gabriel García Márquez",
  "category": "Literatura",
  "isbn": "978-84-376-0494-7",
  "supplier_country": "VE",
  "cost_usd": "25.00",
  "stock_quantity": 50
}
```

`selling_price_local`, `id`, `created_at`, `updated_at` are read-only and ignored on input.

**Success:** `201 Created` — returns the created book object (full schema above).

**Errors:**
- `400 Bad Request` — validation failure: `cost_usd <= 0`, `stock_quantity < 0`, invalid ISBN, duplicate ISBN, or missing/invalid required fields.

---

## GET /books/

List all books, paginated (default page size 10).

**Query parameters:**
- `page` (integer, optional) — page number.

**Success:** `200 OK` — paginated response with `results` array of book objects.

**Errors:** none specific.

---

## GET /books/{id}/

Retrieve a single book by id.

**Success:** `200 OK` — book object.

**Errors:**
- `404 Not Found` — no book with the given id.

---

## PUT /books/{id}/

Fully update an existing book.

**Request body (JSON):** same fields as POST; all writable fields required.

**Success:** `200 OK` — updated book object.

**Errors:**
- `400 Bad Request` — validation failure.
- `404 Not Found` — no book with the given id.

---

## DELETE /books/{id}/

Delete a book by id.

**Success:** `204 No Content`.

**Errors:**
- `404 Not Found` — no book with the given id.

---

## GET /books/search?category=

Search books by category (case-insensitive partial match).

**Query parameters:**
- `category` (string, required) — substring to match against `category`.

**Success:** `200 OK` — paginated response with matching books.

**Errors:**
- `400 Bad Request` — `category` query parameter is missing.

Example: `GET /books/search/?category=Literatura`

---

## GET /books/low-stock?threshold=

List books with `stock_quantity` less than or equal to a threshold.

**Query parameters:**
- `threshold` (integer, optional, default `10`) — non-integer values fall back to `10`.

**Success:** `200 OK` — paginated response with matching books.

Example: `GET /books/low-stock/?threshold=5`

---

## POST /books/{id}/calculate-price/

Calculate the suggested local selling price for a book and persist it.

Formula: `cost_local = cost_usd × exchange_rate`; `selling_price_local = cost_local × 1.40` (40% margin). Results rounded to 2 decimals (half up). The computed price is saved on the book row.

**Request body:** none required.

**Success:** `200 OK` — price calculation result:

```json
{
  "book_id": 1,
  "cost_usd": "25.00",
  "exchange_rate": "36.5",
  "cost_local": "912.50",
  "margin_percentage": 40,
  "selling_price_local": "1277.50",
  "currency": "VES",
  "calculation_timestamp": "2026-01-01T00:00:00Z"
}
```

**Errors:**
- `404 Not Found` — no book with the given id.
- `500 Internal Server Error` — exchange rate unavailable (live API unreachable and no fallback rate in the database).
