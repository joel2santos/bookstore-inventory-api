# Endpoints de la API

URL base: `http://localhost/` (vía Traefik en el puerto 80) o `http://localhost:8000/` (aplicación directamente).
Todas las rutas son relativas a la raíz de la API. `id` es la clave primaria de la base de datos del libro (entero).

## Recurso Libro (JSON)

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

| Campo | Tipo | Notas |
|---|---|---|
| id | entero | Solo lectura, asignado al crear |
| title | cadena | Obligatorio |
| author | cadena | Obligatorio |
| category | cadena | Obligatorio |
| isbn | cadena | Obligatorio, ISBN-10 o ISBN-13 (se permiten guiones/espacios), único |
| supplier_country | cadena | Obligatorio, código de país de 2 caracteres |
| cost_usd | cadena (decimal) | Obligatorio, debe ser > 0 |
| selling_price_local | cadena o nulo | Solo lectura, asignado por calculate-price |
| stock_quantity | entero | Obligatorio, debe ser >= 0 |
| created_at | fecha y hora | Solo lectura |
| updated_at | fecha y hora | Solo lectura |

Las respuestas de lista paginada usan:

```json
{
  "count": 12,
  "next": "http://localhost/books/?page=2",
  "previous": null,
  "results": [ { ...libro... } ]
}
```

Las respuestas de error usan `{ "detail": "<mensaje>" }`.

---

## POST /books/

Crear un libro nuevo.

**Cuerpo de la solicitud (JSON):**

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

`selling_price_local`, `id`, `created_at`, `updated_at` son de solo lectura y se ignoran en la entrada.

**Éxito:** `201 Created` — devuelve el objeto libro creado (esquema completo anterior).

**Errores:**
- `400 Bad Request` — error de validación: `cost_usd <= 0`, `stock_quantity < 0`, ISBN inválido, ISBN duplicado, o campos obligatorios faltantes/inválidos.

---

## GET /books/

Listar todos los libros, paginados (tamaño de página predeterminado 10).

**Parámetros de consulta:**
- `page` (entero, opcional) — número de página.

**Éxito:** `200 OK` — respuesta paginada con arreglo `results` de objetos libro.

**Errores:** ninguno específico.

---

## GET /books/{id}/

Obtener un solo libro por id.

**Éxito:** `200 OK` — objeto libro.

**Errores:**
- `404 Not Found` — no existe libro con el id dado.

---

## PUT /books/{id}/

Actualizar completamente un libro existente.

**Cuerpo de la solicitud (JSON):** mismos campos que POST; todos los campos de escritura obligatorios.

**Éxito:** `200 OK` — objeto libro actualizado.

**Errores:**
- `400 Bad Request` — error de validación.
- `404 Not Found` — no existe libro con el id dado.

---

## DELETE /books/{id}/

Eliminar un libro por id.

**Éxito:** `204 No Content`.

**Errores:**
- `404 Not Found` — no existe libro con el id dado.

---

## GET /books/search?category=

Buscar libros por categoría (coincidencia parcial sin distinción de mayúsculas/minúsculas).

**Parámetros de consulta:**
- `category` (cadena, obligatoria) — subcadena para coincidir con `category`.

**Éxito:** `200 OK` — respuesta paginada con libros coincidentes.

**Errores:**
- `400 Bad Request` — falta el parámetro de consulta `category`.

Ejemplo: `GET /books/search/?category=Literatura`

---

## GET /books/low-stock?threshold=

Listar libros con `stock_quantity` menor o igual a un umbral.

**Parámetros de consulta:**
- `threshold` (entero, opcional, predeterminado `10`) — los valores no enteros recurren a `10`.

**Éxito:** `200 OK` — respuesta paginada con libros coincidentes.

Ejemplo: `GET /books/low-stock/?threshold=5`

---

## POST /books/{id}/calculate-price/

Calcular el precio de venta local sugerido para un libro y persistirlo.

Fórmula: `cost_local = cost_usd × exchange_rate`; `selling_price_local = cost_local × 1.40` (margen del 40 %). Los resultados se redondean a 2 decimales (medio hacia arriba). El precio calculado se guarda en la fila del libro.

**Cuerpo de la solicitud:** ninguno requerido.

**Éxito:** `200 OK` — resultado del cálculo de precio:

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

**Errores:**
- `404 Not Found` — no existe libro con el id dado.
- `500 Internal Server Error` — tipo de cambio no disponible (API en vivo inalcanzable y sin tasa de reserva en la base de datos).
