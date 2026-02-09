# Makefile para Sistema de Inventario Inteligente

.PHONY: help setup dev stop logs clean backup test

help: ## Muestra esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Configuración inicial del proyecto
	@echo "🔧 Configurando proyecto..."
	@if not exist .env (copy .env.example .env && echo "✅ Archivo .env creado. Por favor configurar las variables.") else (echo "⚠️  .env ya existe")
	@echo "✅ Configuración completada"

dev: ## Levantar entorno de desarrollo
	@echo "🚀 Levantando servicios..."
	docker-compose up -d
	@echo "⏳ Esperando a que los servicios estén listos..."
	timeout /t 10 /nobreak > nul
	@echo "✅ Servicios levantados"
	@echo "📝 Inicializando base de datos..."
	docker-compose exec -T backend flask db upgrade
	docker-compose exec -T backend flask seed-data
	@echo "✅ Sistema listo!"
	@echo ""
	@echo "🌐 Accesos:"
	@echo "   Frontend:  http://localhost:3000"
	@echo "   API:       http://localhost:5000"
	@echo "   Swagger:   http://localhost:5000/api/docs"
	@echo "   n8n:       http://localhost:5678"

stop: ## Detener todos los servicios
	@echo "🛑 Deteniendo servicios..."
	docker-compose down
	@echo "✅ Servicios detenidos"

logs: ## Ver logs de todos los servicios
	docker-compose logs -f

logs-backend: ## Ver logs solo del backend
	docker-compose logs -f backend

logs-frontend: ## Ver logs solo del frontend
	docker-compose logs -f frontend

restart: ## Reiniciar todos los servicios
	@echo "🔄 Reiniciando servicios..."
	docker-compose restart
	@echo "✅ Servicios reiniciados"

clean: ## Limpiar contenedores y volúmenes
	@echo "🧹 Limpiando contenedores y volúmenes..."
	docker-compose down -v
	@echo "✅ Limpieza completada"

backup: ## Crear backup de la base de datos
	@echo "💾 Creando backup..."
	@if not exist backups mkdir backups
	docker-compose exec -T postgres pg_dump -U usuario_inventario inventario_db > backups/backup_$(shell powershell -Command "Get-Date -Format 'yyyyMMdd_HHmmss'").sql
	@echo "✅ Backup creado en backups/"

restore: ## Restaurar backup de base de datos (usar: make restore FILE=backup.sql)
	@echo "📥 Restaurando backup..."
	@if "$(FILE)"=="" (echo "❌ Error: Especificar archivo con FILE=nombre.sql" && exit 1)
	docker-compose exec -T postgres psql -U usuario_inventario inventario_db < $(FILE)
	@echo "✅ Backup restaurado"

shell-backend: ## Abrir shell en contenedor backend
	docker-compose exec backend /bin/bash

shell-db: ## Abrir psql en base de datos
	docker-compose exec postgres psql -U usuario_inventario inventario_db

test: ## Ejecutar tests del backend
	docker-compose exec backend pytest tests/ -v

migrate: ## Crear nueva migración de base de datos
	docker-compose exec backend flask db migrate -m "$(MSG)"

upgrade-db: ## Aplicar migraciones pendientes
	docker-compose exec backend flask db upgrade

build: ## Reconstruir imágenes Docker
	@echo "🔨 Reconstruyendo imágenes..."
	docker-compose build
	@echo "✅ Imágenes reconstruidas"

ps: ## Ver estado de los servicios
	docker-compose ps

stats: ## Ver estadísticas de recursos
	docker stats
