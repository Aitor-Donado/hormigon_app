# Contenedores y despliegue con Docker Compose

## Resumen de cambios

- La aplicación Flask ahora utiliza **SQLAlchemy** como ORM y se conecta a una base de datos **PostgreSQL** en lugar de SQLite.
- Las credenciales y parámetros de la base de datos se gestionan mediante **variables de entorno**.
- Se ha añadido un modelo de usuario con SQLAlchemy y la inicialización automática de la base de datos.
- Se ha creado un archivo `docker-compose.yml` que define dos servicios:
  - `db`: contenedor de PostgreSQL con volumen persistente.
  - `web`: contenedor de la app Flask, conectado a la base de datos mediante red interna.
- El archivo `requirements.txt` incluye las dependencias necesarias para PostgreSQL, SQLAlchemy y gestión de variables de entorno.

## Instrucciones para levantar los contenedores

1. **Copia o revisa los archivos:**
   - `app.py` (usa SQLAlchemy y variables de entorno)
   - `requirements.txt` (incluye Flask, Flask-SQLAlchemy, psycopg2-binary, python-dotenv, etc.)
   - `docker-compose.yml` (define los servicios y la red)
   - `Dockerfile` (construye la imagen de la app)

2. **Construye y levanta los contenedores:**
   
   ```bash
   docker-compose up --build
   ```

   Esto descargará la imagen de PostgreSQL, construirá la imagen de la app y levantará ambos servicios en red.

3. **Accede a la aplicación:**
   
   - Abre tu navegador en [http://localhost:5000](http://localhost:5000)

4. **Persistencia de datos:**
   - Los datos de PostgreSQL se guardan en el volumen `pgdata` y no se perderán aunque detengas los contenedores.

5. **Variables de entorno:**
   - Puedes personalizar las credenciales de la base de datos y las claves secretas editando el archivo `docker-compose.yml` o usando un archivo `.env`.

---

**¡Listo! Tu aplicación ahora es más robusta, escalable y lista para producción con Docker y PostgreSQL.** 