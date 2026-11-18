# Criterios de verificación de NFRs

| NFR | Atributo | Escenario medible | Método | Resultado | Observaciones |
|---|---|---|---|---|---|
| NFR-01 | Simplicidad de operación | Obtener una calificación de al menos 8 en la encuesta de simplicidad | Encuesta |  |  |
| NFR-02 | Bajo costo | Costo 0 de licencias y un uso de RAM <= 1.5 GB total | Comando `docker stats --no-stream` | Costo = 0. Uso de memoria = 678.69MB | Conseguido |
| NFR-03 | Trazabilidad y auditabilidad | Obtención de todos los reportes en CSV y testeo de no poder eliminar las entregas de la BD | Test unitarios con el comando `docker compose run --rm app python manage.py test apps.comedores apps.deposito apps.entregas -v 2` | Todos los test pasaron | Conseguido |
| NFR-04 | Mantenibilidad / modificabilidad | Cant. de librerías <= 10 justificadas y pasar el 100% de los test de arquitectura | Django Test con el comando `docker compose run --rm app python manage.py test apps.tests` | Todos los test pasaron. Hay un total de 5 librerías | Conseguido |



### Justificación de Librerías usadas

| Librería | Justificación |
|----------|---------------|
| Django | Framework central de la aplicación. ORM, integración con SQLite, migraciones, SSR para HTML, sesiones, autenticación y tests. |
| Django-ninja | Armado de la API REST con OpenAPI, errores en formato RFC 9457 y armado automático del Swagger UI |
| mozilla-django-oidc | Conexión con OpenID (OIDC), integración con Keycloak |
| whitenoise | Manejo de archivos CSS dentro de Python |
| gunicorn | Servidor HTTP WSGI en Python |

### Librerías del simulador de Padrón

| Librería | Justificación |
|----------|---------------|
| fastapi | Arma el mock API REST con latencia configurable e inyección de errores |
| uvicorn | Servidor que corre FastAPI para exponer el servicio |