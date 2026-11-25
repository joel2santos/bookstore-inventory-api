# Postman Collection
## How to import

1. Open Postman.
2. Click **Import** → **Upload Files**.
3. Select `./postman.json`.
4. The collection appears in your Postman sidebar.

## Environment variables

Set these in your Postman environment (or use the collection-level variables):

| Variable | Example value | Description |
|----------|---------------|-------------|
| `baseUrl` | `http://localhost` | API base URL (Traefik routes to port 80) |
| `bookId` | `1` | ID of the book for detail/update/delete/calculate-price |
| `category` | `Literatura` | Category filter for the search endpoint |
| `threshold` | `10` | Low-stock threshold filter |

## Endpoints included

| Folder | Request | Method | Path |
|--------|---------|--------|------|
| CRUD | Create Book | POST | `/books/` |
| CRUD | List Books | GET | `/books/` |
| CRUD | Get Book by ID | GET | `/books/{id}/` |
| CRUD | Update Book | PUT | `/books/{id}/` |
| CRUD | Delete Book | DELETE | `/books/{id}/` |
| Search & Filters | Search by Category | GET | `/books/search?category=` |
| Search & Filters | Low Stock | GET | `/books/low-stock?threshold=` |
| Price Calculation | Calculate Selling Price | POST | `/books/{id}/calculate-price/` |

## Test scripts included

Each request has a Postman test script that verifies:

- HTTP status code (200, 201, 204 as appropriate)
- Create Book: response has an `id`, stores it in the `bookId` collection variable
- Calculate Selling Price: response contains `selling_price_local`, `currency` is `"VES"`, `margin_percentage` is `40`

## Run

1. Start the stack: `docker compose up -d --build`
2. In Postman, select your environment with `baseUrl = http://localhost`.
3. Send requests in order: Create → List → Get → Update → Delete (or any order).
4. For Calculate Price, ensure a book exists first (use the ID from Create).
