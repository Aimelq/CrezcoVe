# Guía de Instalación - Sistema de Inventario Inteligente

## 📋 Requisitos del Sistema

### Hardware Mínimo
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disco**: 10 GB libres

### Software Requerido
- **Docker Desktop** 20.10 o superior
- **Docker Compose** 2.0 o superior
- **Git** (opcional, para clonar el repositorio)

## 🚀 Instalación Paso a Paso

### 1. Obtener el Código

Si tienes Git instalado:
```bash
git clone <url-repositorio>
cd Sistema-Inventario-Inteligente
```

Si no tienes Git, descarga el ZIP y extráelo.

### 2. Configurar Variables de Entorno

Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

Edita `.env` con un editor de texto y configura:

#### Variables Obligatorias

```env
# Base de Datos
DB_PASSWORD=TU_PASSWORD_SEGURO_AQUI

# JWT
SECRET_KEY=GENERAR_CON_OPENSSL
JWT_SECRET_KEY=GENERAR_CON_OPENSSL

# n8n
N8N_PASSWORD=TU_PASSWORD_N8N
```

#### Generar Claves Seguras

En PowerShell:
```powershell
# Para SECRET_KEY y JWT_SECRET_KEY
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

O usa un generador online: https://randomkeygen.com/

#### Variables de Telegram (Opcional)

Para usar el bot de Telegram:

1. Habla con @BotFather en Telegram
2. Crea un nuevo bot con `/newbot`
3. Copia el token que te da
4. Pégalo en `TELEGRAM_BOT_TOKEN`

Para obtener tu Chat ID:
1. Habla con @userinfobot en Telegram
2. Copia el ID que te muestra
3. Pégalo en `TELEGRAM_CHAT_ID_DUENO`

### 3. Levantar los Servicios

```bash
docker-compose up -d
```

Esto descargará las imágenes necesarias (puede tomar varios minutos la primera vez).

### 4. Verificar que los Servicios Estén Corriendo

```bash
docker-compose ps
```

Deberías ver todos los servicios en estado "Up":
- postgres
- redis
- backend
- celery_worker
- celery_beat
- frontend (si está implementado)
- n8n

### 5. Inicializar la Base de Datos

```bash
docker-compose exec backend flask db upgrade
docker-compose exec backend flask seed-data
```

Esto creará las tablas y cargará datos iniciales.

### 6. Acceder al Sistema

Abre tu navegador en:
- **API**: http://localhost:5000
- **Documentación Swagger**: http://localhost:5000/api/docs
- **n8n**: http://localhost:5678
- **Frontend**: http://localhost:3000 (cuando esté implementado)

### 7. Iniciar Sesión

Credenciales por defecto:
- **Email**: admin@inventario.com
- **Password**: admin123

⚠️ **IMPORTANTE**: Cambia estas credenciales inmediatamente en producción.

## 🔧 Solución de Problemas

### Error: "Port already in use"

Si algún puerto está ocupado, puedes cambiarlos en `docker-compose.yml`:

```yaml
ports:
  - "5001:5000"  # Cambiar el primer número
```

### Error: "Cannot connect to database"

Espera unos segundos más. PostgreSQL puede tardar en inicializarse.

Verifica el estado:
```bash
docker-compose logs postgres
```

### Error: "Permission denied"

En Windows, asegúrate de que Docker Desktop esté corriendo con permisos de administrador.

### Ver Logs de Errores

```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo base de datos
docker-compose logs -f postgres
```

## 🔄 Comandos Útiles

### Detener el Sistema
```bash
docker-compose down
```

### Reiniciar un Servicio
```bash
docker-compose restart backend
```

### Limpiar Todo (⚠️ Elimina datos)
```bash
docker-compose down -v
```

### Crear Backup de Base de Datos
```bash
docker-compose exec postgres pg_dump -U usuario_inventario inventario_db > backup.sql
```

### Restaurar Backup
```bash
docker-compose exec -T postgres psql -U usuario_inventario inventario_db < backup.sql
```

## 📦 Instalación en Producción

### Diferencias Importantes

1. **Usar docker-compose.prod.yml** (cuando esté disponible)
2. **Configurar HTTPS** con certificados SSL
3. **Cambiar todas las contraseñas** por defecto
4. **Configurar firewall** para exponer solo puertos necesarios
5. **Configurar backups automáticos**

### Variables de Entorno en Producción

```env
FLASK_ENV=production
DEBUG=False
```

### Recomendaciones de Seguridad

- ✅ Usar contraseñas fuertes (mínimo 16 caracteres)
- ✅ Cambiar credenciales por defecto
- ✅ Configurar HTTPS/SSL
- ✅ Limitar acceso a puertos internos
- ✅ Configurar backups automáticos diarios
- ✅ Monitorear logs de seguridad

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker-compose logs -f`
2. Verifica que todos los servicios estén corriendo: `docker-compose ps`
3. Consulta la documentación completa
4. Abre un issue en GitHub

## ✅ Verificación de Instalación

Para verificar que todo funciona correctamente:

1. Accede a http://localhost:5000/api/docs
2. Deberías ver la documentación Swagger
3. Prueba el endpoint `/api/auth/login` con las credenciales por defecto
4. Si obtienes un token JWT, ¡todo está funcionando!

---

¡Felicidades! Tu Sistema de Inventario Inteligente está listo para usar. 🎉
