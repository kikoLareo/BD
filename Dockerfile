# Utilizar una imagen base de Python
FROM python:3.10-slim

# Configurar directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir email-validator python-jose python-dotenv python-multipart

# Copiar el código del proyecto
COPY . .

# Exponer el puerto
EXPOSE 8000

# Ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
