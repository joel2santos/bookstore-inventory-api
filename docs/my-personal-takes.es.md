## Lo que cambiaría

**#1 — Almacenar precios en caché en Redis en lugar de persistirlos en la BD**
`selling_price_local` se escribe actualmente en la fila `Book`. Dada la volátil economía de Venezuela, los precios se vuelven obsoletos rápidamente. Un caché de Redis con TTL de 24 horas reflejaría los cambios de tasa más rápido y evitaría reescribir filas de libro en cada cálculo.

**#2 — Usar Go en lugar de Django**
El modelo de concurrencia de Go se adapta mejor al manejo de solicitudes de API que el ciclo de solicitud/respuesta de Django.

**#3 — Observabilidad y datos del cliente**
Implementar una pila PLG (Prometheus, Loki, Grafana) para observabilidad, y una herramienta tipo Jitsu para la recopilación de datos del cliente. Ninguna existe en el proyecto hoy (la observabilidad está fuera de alcance).

**#4 — Otras observaciones**

- Recomendaría usar UUIDs para los identificadores de libros en lugar de enteros, ya que los UUIDs son más difíciles de adivinar y proporcionan un nivel adicional de seguridad.
- gunicorn se usa en lugar de `runserver` de Django para servir (3 trabajadores, tiempo de espera 120 s).
- `Decimal` se usa para el dinero (`cost_usd`, `selling_price_local`, matemática de tipo de cambio) en lugar de float, evitando errores de redondeo de punto flotante.
