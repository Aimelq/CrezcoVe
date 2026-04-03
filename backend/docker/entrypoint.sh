#!/bin/bash
set -e

echo "🚀 Iniciando aplicación Flask..."

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a PostgreSQL en ${DB_HOST:-postgres}:${DB_PORT:-5432}..."
while ! pg_isready -h "${DB_HOST:-postgres}" -p "${DB_PORT:-5432}" -U "${DB_USER:-usuario_inventario}" > /dev/null 2>&1; do
    sleep 2
done
echo "✅ PostgreSQL está listo"

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
