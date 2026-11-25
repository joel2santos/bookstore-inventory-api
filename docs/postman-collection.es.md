# Colección de Postman
## Cómo importar

1. Abre Postman.
2. Haz clic en **Import** → **Upload Files**.
3. Selecciona `./postman.json`.
4. La colección aparecerá en la barra lateral de Postman.

## Variables de entorno

Configura estas variables en tu entorno de Postman (o usa las variables a nivel de colección):

| Variable | Valor ejemplo | Descripción |
|----------|---------------|-------------|
| `baseUrl` | `http://localhost` | URL base de la API (Traefik enruta al puerto 80) |
| `bookId` | `1` | ID del libro para detalle/actualizar/eliminar/calcular-precio |
| `category` | `Literatura` | Filtro de categoría para el endpoint de búsqueda |
| `threshold` | `10` | Umbral de filtro de stock bajo |

## Endpoints incluidos

| Carpeta | Solicitud | Método | Ruta |
|---------|-----------|--------|------|
| CRUD | Create Book | POST | `/books/` |
| CRUD | List Books | GET | `/books/` |
| CRUD | Get Book by ID | GET | `/books/{id}/` |
| CRUD | Update Book | PUT | `/books/{id}/` |
| CRUD | Delete Book | DELETE | `/books/{id}/` |
| Search & Filters | Search by Category | GET | `/books/search?category=` |
| Search & Filters | Low Stock | GET | `/books/low-stock?threshold=` |
| Price Calculation | Calculate Selling Price | POST | `/books/{id}/calculate-price/` |

## Scripts de prueba incluidos

Cada solicitud tiene un script de prueba de Postman que verifica:

- Código de estado HTTP (200, 201, 204 según corresponda)
- Create Book: la respuesta tiene un `id`, lo guarda en la variable de colección `bookId`
- Calculate Selling Price: la respuesta contiene `selling_price_local`, `currency` es `"VES"`, `margin_percentage` es `40`

## Ejecutar

1. Inicia la pila: `docker compose up -d --build`
2. En Postman, selecciona tu entorno con `baseUrl = http://localhost`.
3. Envía las solicitudes en orden: Crear → Listar → Obtener → Actualizar → Eliminar (o cualquier orden).
4. Para Calcular Precio, asegúrate de que exista un libro primero (usa el ID de Crear).
