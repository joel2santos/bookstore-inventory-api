# API de Inventario de Librería

API REST para una cadena de librerías que gestione su inventario, valide precios con tipos de cambio en vivo y calcule precios de venta sugeridos.

> **Nota:** La versión en inglés de este documento está en `README.en.md`.

## Requisitos del Proyecto

**Funcionales:**
- Gestionar el inventario de libros (CRUD: crear, listar, obtener, actualizar, eliminar)
- Validar precios con tipos de cambio en vivo USD → moneda local
- Calcular precio de venta sugerido (costo × tipo de cambio × margen 40%)
- Buscar libros por categoría
- Filtrar libros por stock bajo

**Stack tecnológico:**
- Python 3.11
- Django 5.2
- Django REST Framework
- PostgreSQL 15
- Docker & Docker Compose
- Traefik v2.11 (reverse proxy)
- gunicorn (WSGI de producción)

## Instalación y Ejecución

### Requisitos previos
- Docker y Docker Compose instalados

### Ejecutar con Docker Compose

```bash
# Copiar la plantilla de entorno
cp .env.example .env

# Editar .env con sus valores (ver explicaciones de .env abajo)
# Al menos configurar SECRET_KEY a un valor aleatorio fuerte

# Construir e iniciar
docker compose up -d --build

# La API está disponible en http://localhost/ (vía Traefik en el puerto 80)

# Detener
docker compose down

# Detener y eliminar volúmenes
docker compose down -v
```

### Ejecutar pruebas

```bash
SECRET_KEY=k DEBUG=True DJANGO_SETTINGS_MODULE=config.test_settings .venv/bin/python manage.py test interface.api.books -v 2
```

### Poblar la base de datos (Seeding)

Para poblar la base de datos con libros de prueba utilizando el script de seeding:

**Dentro del contenedor de la aplicación:**
```bash
docker compose exec app python scripts/seed_books.py --count 100
```

**Contra la API HTTP en ejecución desde el host:**
```bash
python scripts/seed_books.py --mode api --count 40 --base-url http://localhost/api
```

Parámetros opcionales disponibles:
- `--count N`: Número de libros a generar (por defecto: 60)
- `--seed N`: Semilla aleatoria para reproducibilidad
- `--mode MODE`: Método de inserción (`db` para ORM de Django directo o `api` para solicitudes HTTP POST)
- `--base-url URL`: URL base de la API al usar `--mode api` (por defecto: `http://localhost/api`)

## Explicaciones de .env

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| SECRET_KEY | Clave criptográfica de firma de Django. **Obligatoria** - No hay valor por defecto. Generar un valor aleatorio fuerte. | django-insecure-changeme-in-prod |
| DEBUG | Modo depuración de Django. Por defecto `False`. Configurar `True` solo en desarrollo local. | True |
| ALLOWED_HOSTS | Lista separada por comas de nombres de host/dominio permitidos. | localhost,127.0.0.1 |
| DB_NAME | Nombre de la base de datos PostgreSQL. | bookstore_inventory |
| DB_USER | Usuario de PostgreSQL. | postgres |
| DB_PASSWORD | Contraseña de PostgreSQL. | postgres |
| DB_HOST | Host de PostgreSQL. Dentro de Compose, usar el nombre del servicio `db`. | db |
| DB_PORT | Puerto de PostgreSQL. | 5432 |
| EXCHANGE_RATE_API_URL | Endpoint de la API externa de tipos de cambio. | https://api.exchangerate-api.com/v4/latest/USD |
| DEFAULT_LOCAL_CURRENCY | Moneda objetivo predeterminada para la conversión de precios (se la tasa de respaldo en la BD). | VES |


## Ejemplos de Endpoints

URL base: http://localhost/ (Traefik enruta internamente a la app)

### Crear un libro
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

### Listar libros (paginado)
```bash
curl http://localhost/books/?page=1
# → 200 OK, {"count":..., "next":null, "previous":null, "results":[...]}
```

### Obtener libro por ID
```bash
curl http://localhost/books/1/
# → 200 OK
```

### Actualizar un libro
```bash
curl -X PUT http://localhost/books/1/ \
  -H "Content-Type: application/json" \
  -d '{"title": "El Quijote (editado)", "stock_quantity": 30}'
# → 200 OK
```

### Eliminar un libro
```bash
curl -X DELETE http://localhost/books/1/
# → 204 No Content
```

### Buscar por categoría
```bash
curl "http://localhost/books/search?category=Literatura"
# → 200 OK, resultados paginados que coincidan con la categoría (icontains)
```

### Filtrar stock bajo
```bash
curl "http://localhost/books/low-stock?threshold=10"
# → 200 OK, libros con stock_quantity <= 10
# El umbral predeterminado es 10 si se omite
```

### Calcular precio de venta sugerido
```bash
curl -X POST http://localhost/books/1/calculate-price/
# → 200 OK, {"book_id":1,"cost_usd":"15.99","exchange_rate":"922.56","cost_local":"14751.73","margin_percentage":40,"selling_price_local":"20652.42","currency":"VES","calculation_timestamp":"2026-11-25T00:48:32Z"}
```

El cálculo de precio persiste `selling_price_local` en el registro del libro. Si la API externa de tipos de cambio no está disponible, usa la tasa de respaldo almacenada en la tabla de base de datos `ExchangeRateConfig` (seeda desde `DEFAULT_LOCAL_CURRENCY`).

## Arquitectura

Arquitectura limpia con cuatro capas:
- domain/books/ — entidades y excepciones sin dependencia de framework
- application/books/ — servicios de caso de uso e interfaces abstractas
- infrastructure/db/ — modelos ORM de Django e implementación del repositorio
- infrastructure/external/ — gateway de tasa de cambio externa
- interface/api/books/ — serializadores, vistas y URLs de DRF

No se configura autenticación (por decisión de diseño). Se aplica limitación de tasa globalmente (anon: 100/día, user: 1000/día).
