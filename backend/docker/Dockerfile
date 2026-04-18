FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requirements
COPY requirements/*.txt ./requirements/

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/base.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio para uploads
RUN mkdir -p /app/uploads && chmod 755 /app/uploads

# Crear usuario no root
RUN useradd -m -u 1000 usuario_app && \
    chown -R usuario_app:usuario_app /app

USER usuario_app

# Exponer puerto
EXPOSE 5000

# Script de inicio
COPY docker/entrypoint.sh /entrypoint.sh
USER root
RUN chmod +x /entrypoint.sh && sed -i 's/\r$//' /entrypoint.sh
USER usuario_app

ENTRYPOINT ["/entrypoint.sh"]
