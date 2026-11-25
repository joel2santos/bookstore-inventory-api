# Alcance del proyecto

## Contexto de negocio

Una API de inventario de librerías que rastrea libros, su costo en USD, niveles de stock y categoría.
Capacidades principales:

- Mantener libros (crear, listar, obtener, actualizar, eliminar).
- Buscar libros por categoría.
- Listar libros con stock bajo (por debajo de un umbral).
- Calcular y persistir un precio de venta local sugerido: `cost_local = cost_usd × exchange_rate`, luego `selling_price_local = cost_local × 1.40` (margen del 40 %).
- El tipo de cambio se obtiene de una API JSON en vivo, con una tasa de reserva almacenada en la base de datos para que el negocio pueda actualizarla sin volver a implementar.

## Pila tecnológica

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.11 |
| Framework web | Django 5.2 |
| Framework de API | Django REST Framework |
| Base de datos | PostgreSQL 15 |
| Orquestación de contenedores | Docker Compose |
| Proxy inverso / entrada | Traefik v2.11 |
| Servidor WSGI | gunicorn |
| Controlador de BD | psycopg2-binary |
| Cliente HTTP | requests |

## Arquitectura

Arquitectura limpia con cuatro capas:

- **`domain/`** — entidades Python simples (`Book`) y excepciones (`BookNotFound`, `ExchangeRateUnavailable`, etc.). Sin dependencias de framework.
- **`application/`** — servicios de caso de uso (`CalculateSellingPrice`) e interfaces abstractas de repositorio/pasarela (`AbstractBookRepository`, `AbstractExchangeRateGateway`).
- **`infrastructure/`** — modelos de Django ORM y repositorio (`DjangoBookRepository`), pasarela externa (`ExchangeRateGateway`) que llama a la API de tipos de cambio con una reserva en la BD.
- **`interface/api/`** — `BookViewSet`, serializadores y enrutamiento de URL de DRF.

Las dependencias apuntan hacia adentro: interface e infrastructure dependen de application y domain, nunca al revés.

## Reglas de negocio

- `cost_usd` debe ser estrictamente positivo (> 0).
- `stock_quantity` debe ser no negativo (>= 0).
- ISBN debe ser un ISBN-10 o ISBN-13 válido (se verifica el dígito de control; se permiten guiones y espacios) y es único entre libros.
- El margen sugerido es del 40 % sobre el costo local.
- La moneda local predeterminada es VES (bolívar venezolano), sustituible mediante `DEFAULT_LOCAL_CURRENCY`.
- Tipo de cambio: API en vivo primero, luego la fila singleton `ExchangeRateConfig` en la base de datos como reserva.

## Fuera de alcance

- Autenticación / autorización (ninguna, por decisión del usuario) — todos los endpoints están abiertos.
- Interfaz de frontend o de administración para usuarios finales.
- Pila WSGI de producción más allá de gunicorn.
- Observabilidad (métricas, trazado, infraestructura de registro).
