# Sistema de Inventario Inteligente

Sistema completo de gestión de inventario para PYMEs con panel web React, API Flask, bot de Telegram y automatizaciones n8n.

## 🚀 Características Principales

### Funcionalidades Inteligentes
- ✅ **Cálculo de Costo Promedio Ponderado**: Actualización automática de costos en cada compra
- ✅ **Predicción de Agotamiento**: Análisis de ventas históricas para predecir cuándo se agotará un producto
- ✅ **Asistente de Precios**: Detecta inflación y sugiere ajustes de precio para mantener márgenes
- ✅ **Auditoría Ciega Anti-Robo**: Selección aleatoria de productos para conteo físico
- ✅ **Reporte de Dinero Dormido**: Identifica productos sin movimiento que inmovilizan capital
- ✅ **Logs de Seguridad "Caja Negra"**: Registro inmutable de todas las acciones del sistema

### Stack Tecnológico
- **Frontend**: React 18 + Vite + TypeScript + Tailwind CSS + Shadcn/UI
- **Backend**: Flask + SQLAlchemy + PostgreSQL + Redis + Celery
- **Automatización**: n8n + Bot de Telegram
- **Infraestructura**: Docker + Docker Compose

## 📋 Requisitos Previos

- Docker y Docker Compose instalados
- Al menos 4GB de RAM disponible
- Puertos disponibles: 3000, 5000, 5432, 6379, 5678

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <url-repositorio>
cd Sistema-Inventario-Inteligente
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
```

Editar `.env` y configurar:
- Contraseñas de base de datos
- Claves secretas JWT
- Token de bot de Telegram (obtener de @BotFather)
- IDs de chat de Telegram (obtener de @userinfobot)

### 3. Levantar servicios con Docker
```bash
docker-compose up -d
```

### 4. Inicializar base de datos
```bash
docker-compose exec backend flask db upgrade
docker-compose exec backend flask seed-data
```

## 🎯 Acceso a los Servicios

- **Frontend**: http://localhost:3000
- **API Backend**: http://localhost:5000
- **Documentación API (Swagger)**: http://localhost:5000/api/docs
- **n8n**: http://localhost:5678

### Credenciales por defecto
- **Email**: admin@inventario.com
- **Password**: admin123

⚠️ **IMPORTANTE**: Cambiar estas credenciales en producción

## 📚 Estructura del Proyecto

```
Sistema-Inventario-Inteligente/
├── backend/              # API Flask
│   ├── app/
│   │   ├── api/         # Endpoints REST
│   │   ├── models/      # Modelos SQLAlchemy
│   │   ├── services/    # Servicios inteligentes
│   │   └── core/        # Configuración
│   └── requirements/    # Dependencias Python
├── frontend/            # Aplicación React
│   └── src/
│       ├── components/  # Componentes React
│       ├── pages/       # Páginas
│       └── api/         # Cliente API
├── n8n/                 # Workflows de automatización
│   └── workflows/       # Workflows exportados
└── docker-compose.yml   # Configuración Docker
```

## 🔌 API Endpoints

### Autenticación
- `POST /api/auth/registro` - Registrar usuario
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/logout` - Cerrar sesión
- `POST /api/auth/refresh` - Refrescar token

### Productos
- `GET /api/productos` - Listar productos
- `POST /api/productos` - Crear producto
- `GET /api/productos/{id}` - Obtener producto
- `PUT /api/productos/{id}` - Actualizar producto
- `DELETE /api/productos/{id}` - Eliminar producto
- `GET /api/productos/{id}/prediccion-agotamiento` - Predicción de agotamiento
- `GET /api/productos/{id}/historial` - Historial de movimientos

### Inventario
- `POST /api/inventario/ingreso` - Registrar compra
- `POST /api/inventario/salida` - Registrar venta
- `POST /api/inventario/ajuste` - Registrar ajuste/merma
- `POST /api/inventario/auditoria-ciega` - Iniciar auditoría
- `GET /api/inventario/balance` - Balance actual
- `GET /api/inventario/reporte-dinero-dormido` - Productos sin movimiento

### Proveedores
- `GET /api/proveedores` - Listar proveedores
- `POST /api/proveedores` - Crear proveedor
- `GET /api/proveedores/{id}/pedido-sugerido` - Generar pedido inteligente

### Reportes
- `GET /api/reportes/dashboard` - Datos para dashboard
- `GET /api/reportes/movimientos-7-dias` - Movimientos recientes
- `GET /api/reportes/productos-criticos` - Productos que requieren atención

## 🤖 Bot de Telegram

### Comandos Disponibles
- `/start` - Iniciar bot
- `/stock [codigo]` - Consultar stock
- `/stock_bajo` - Ver productos con stock bajo
- `/ventas_hoy` - Resumen de ventas del día
- `/balance` - Balance del inventario
- `/proveedores` - Listar proveedores

## 🔄 Automatizaciones n8n

### Workflows Configurados
1. **Alerta de Stock Bajo**: Notifica cada hora sobre productos críticos
2. **Reporte Diario**: Envía resumen diario a las 21:00
3. **Auditoría Ciega**: Selecciona productos aleatorios lunes a viernes
4. **Backup Automático**: Backup semanal de base de datos

## 🧪 Desarrollo

### Ejecutar en modo desarrollo
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements/dev.txt
flask run

# Frontend
cd frontend
npm install
npm run dev
```

### Ejecutar tests
```bash
# Backend
pytest tests/

# Frontend
npm run test
```

## 📖 Documentación Adicional

- [Guía de Instalación](docs/INSTALACION.md)
- [Documentación de API](docs/API.md)
- [Guía de Usuario](docs/GUIA_USUARIO.md)

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👥 Soporte

Para soporte y preguntas:
- Abrir un issue en GitHub
- Email: soporte@inventario.com

---

Desarrollado con ❤️ para PYMEs
