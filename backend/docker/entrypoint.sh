#!/bin/bash
set -e

echo "🚀 Iniciando aplicación Flask..."

# Esperar a que PostgreSQL esté listo
echo "⏳ Intentando conectar a la base de datos en ${DB_HOST:-postgres}:${DB_PORT:-5432}..."
max_intentos=30
contador=0

while ! pg_isready -h "${DB_HOST:-postgres}" -p "${DB_PORT:-5432}" -U "${DB_USER:-usuario_inventario}" > /dev/null 2>&1; do
    contador=$((contador+1))
    if [ $contador -gt $max_intentos ]; then
        echo "❌ ERROR: No se pudo conectar a la base de datos después de ${max_intentos} intentos."
        echo "⚠️  Verifica que la base de datos en ${DB_HOST} sea accesible desde este contenedor."
        exit 1
    fi
    echo "⏳ [Intento $contador/$max_intentos] Esperando a PostgreSQL..."
    sleep 2
done
echo "✅ PostgreSQL está listo. Procediendo..."

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones de base de datos..."
flask db upgrade || echo "⚠️  No hay migraciones pendientes"

# Iniciar aplicación
echo "✅ Iniciando servidor..."
if [ "$FLASK_ENV" = "development" ]; then
    echo "🛠️ Modo DESARROLLO detectado - Hot Reloading activado"
    # Usar flask run con debug para recarga automática
    # FLASK_APP ya viene del entorno en docker-compose.yml
    exec flask run --host=0.0.0.0 --port=5000 --debug
else
    echo "📦 Modo PRODUCCIÓN detectado"
    exec gunicorn --bind 0.0.0.0:5000 \
        --workers 2 \
        --threads 4 \
        --timeout 240 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        "app:create_app()"
fi
