# Códigos de error

Todas las respuestas de error son JSON: `{ "detail": "<mensaje>" }`.

## 400 Solicitud incorrecta

Error de validación de entrada. La solicitud no se procesó.

Posibles causas y mensajes:

| Causa | Mensaje de ejemplo |
|---|---|
| `cost_usd` es cero o negativo | `cost_usd must be greater than 0` |
| `stock_quantity` es negativo | `stock_quantity must be greater than or equal to 0` |
| ISBN no es un ISBN-10 o ISBN-13 válido (falla el dígito de control) | `Invalid ISBN` / `Invalid ISBN-10 check digit` / `Invalid ISBN-13 check digit` |
| ISBN ya existe (restricción de unicidad) | `book with this isbn already exists.` |
| Campo obligatorio faltante o en blanco (p. ej. `category`) | `<field>: This field is required.` / `This field may not be blank.` |
| Falta el parámetro de consulta `category` en `/books/search/` | `category query parameter is required` |

Se aplica a: `POST /books/`, `PUT /books/{id}/`, `GET /books/search/`.

## 404 No encontrado

No existe ningún libro con el `id` solicitado.

Mensaje de ejemplo: `Book not found`.

Se aplica a: `GET /books/{id}/`, `PUT /books/{id}/`, `DELETE /books/{id}/`, `POST /books/{id}/calculate-price/`.

## 429 Demasiadas solicitudes

Límite de velocidad excedido (limitación de DRF, configurada en `config.settings`):

| Tipo de cliente | Límite |
|---|---|
| Anónimo | 100 solicitudes/día |
| Usuario autenticado | 1000 solicitudes/día |

No se implementa autenticación en este proyecto, por lo que las solicitudes están efectivamente limitadas por la identidad del cliente tal como la resuelve DRF.

Se aplica a: todos los endpoints.

## 500 Error interno del servidor

Fallo del lado del servidor.

Causa específica manejada por este proyecto:

| Causa | Mensaje |
|---|---|
| Tipo de cambio no disponible | `Exchange rate unavailable` |

El endpoint calculate-price obtiene una tasa en vivo de `EXCHANGE_RATE_API_URL` y recurre a la fila `ExchangeRateConfig` en la base de datos. Si la API en vivo no está alcanzable **y** no hay ninguna tasa de reserva configurada en la base de datos, la solicitud falla con `500`.

Se aplica a: `POST /books/{id}/calculate-price/`.
