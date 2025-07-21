# Usa una imagen base de Python
FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de requisitos e instala las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos
COPY . .

# Expón el puerto donde Flask escucha (normalmente 5000)
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python3", "app.py"]