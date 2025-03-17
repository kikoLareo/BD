FROM python:3.12-slim

# Instalar dependencias del sistema si necesitas psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev

# Crear el directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Comando para arrancar FastAPI con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
