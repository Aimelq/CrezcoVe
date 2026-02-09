# Guía de Configuración del Bot de Telegram

Esta guía te ayudará a configurar el bot de Telegram paso a paso.

## Paso 1: Crear el Bot

1. Abre Telegram y busca **@BotFather**
2. Envía el comando `/newbot`
3. BotFather te pedirá un nombre para tu bot (ejemplo: "Mi Inventario Bot")
4. Luego te pedirá un username (debe terminar en 'bot', ejemplo: "mi_inventario_bot")
5. **¡Importante!** Copia el token que te proporciona. Se verá así:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

## Paso 2: Obtener tu Chat ID

### Opción 1: Usando @userinfobot

1. Busca **@userinfobot** en Telegram
2. Inicia una conversación con `/start`
3. El bot te enviará tu información, incluyendo tu **Chat ID**
4. Copia el número (ejemplo: `123456789`)

### Opción 2: Usando el bot que creaste

1. Inicia una conversación con tu bot (el que creaste con BotFather)
2. Envía cualquier mensaje
3. Abre esta URL en tu navegador (reemplaza TU_TOKEN):
   ```
   https://api.telegram.org/botTU_TOKEN/getUpdates
   ```
4. Busca el campo `"chat":{"id":123456789}` y copia ese número

## Paso 3: Configurar Variables de Entorno

1. Abre el archivo `.env` en la raíz del proyecto
2. Agrega o actualiza estas líneas:

```env
# Bot de Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID_DUENO=123456789
TELEGRAM_CHAT_IDS_EMPLEADOS=987654321,456789123
```

**Explicación**:
- `TELEGRAM_BOT_TOKEN`: El token que te dio BotFather
- `TELEGRAM_CHAT_ID_DUENO`: Tu Chat ID (el dueño del negocio)
- `TELEGRAM_CHAT_IDS_EMPLEADOS`: Chat IDs de empleados, separados por comas (opcional)

## Paso 4: Iniciar el Bot

### Con Docker (Recomendado)

```bash
docker-compose up -d telegram_bot
```

### Localmente (Para desarrollo)

```bash
cd backend
python bot_telegram.py
```

## Paso 5: Probar el Bot

1. Abre Telegram y busca tu bot
2. Envía el comando `/start`
3. Deberías recibir un mensaje de bienvenida
4. Prueba otros comandos:
   ```
   /help
   /balance
   /stock_bajo
   ```

## Comandos Disponibles

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/start` | Mensaje de bienvenida | `/start` |
| `/help` | Lista de comandos | `/help` |
| `/stock [codigo]` | Consultar stock de un producto | `/stock PROD-001` |
| `/stock_bajo` | Ver productos con stock bajo | `/stock_bajo` |
| `/ventas_hoy` | Resumen de ventas del día | `/ventas_hoy` |
| `/balance` | Balance del inventario | `/balance` |
| `/criticos` | Productos críticos | `/criticos` |
| `/proveedores` | Listar proveedores | `/proveedores` |

## Notificaciones Automáticas

Una vez configurado, recibirás notificaciones automáticas para:

- ⚠️ **Stock Bajo**: Cuando un producto alcanza el stock mínimo
- 🔴 **Producto por Agotarse**: Predicción de agotamiento
- 🚨 **Discrepancia en Auditoría**: Diferencias detectadas
- 📈 **Inflación Detectada**: Aumento de costos
- 📊 **Reporte Diario**: Resumen al final del día (21:00)

## Troubleshooting

### El bot no responde

**Problema**: Envío mensajes pero no recibo respuesta

**Soluciones**:
1. Verifica que el bot esté corriendo:
   ```bash
   docker-compose ps telegram_bot
   ```
2. Revisa los logs:
   ```bash
   docker-compose logs telegram_bot
   ```
3. Confirma que el token sea correcto en `.env`

### "No estás autorizado"

**Problema**: El bot responde "No estás autorizado para usar este bot"

**Soluciones**:
1. Verifica que tu Chat ID esté en `TELEGRAM_CHAT_ID_DUENO` o `TELEGRAM_CHAT_IDS_EMPLEADOS`
2. Reinicia el bot después de cambiar el `.env`:
   ```bash
   docker-compose restart telegram_bot
   ```

### No recibo notificaciones

**Problema**: El bot responde a comandos pero no envía notificaciones automáticas

**Soluciones**:
1. Verifica que Celery esté corriendo:
   ```bash
   docker-compose ps celery_worker celery_beat
   ```
2. Asegúrate de haber iniciado una conversación con el bot (`/start`)
3. Revisa los logs de Celery:
   ```bash
   docker-compose logs celery_worker celery_beat
   ```

### Error de base de datos

**Problema**: El bot muestra errores al consultar datos

**Soluciones**:
1. Verifica que PostgreSQL esté corriendo:
   ```bash
   docker-compose ps postgres
   ```
2. Confirma que la URL de base de datos sea correcta
3. Ejecuta las migraciones:
   ```bash
   docker-compose exec backend flask db upgrade
   ```

## Seguridad

### Mejores Prácticas

1. **Nunca compartas tu token**: Es como una contraseña
2. **Limita los Chat IDs autorizados**: Solo agrega personas de confianza
3. **Revoca el token si se compromete**: Usa `/revoke` en BotFather
4. **Usa variables de entorno**: Nunca hardcodees el token en el código

### Revocar y Crear Nuevo Token

Si crees que tu token fue comprometido:

1. Habla con @BotFather
2. Envía `/mybots`
3. Selecciona tu bot
4. Click en "API Token"
5. Click en "Revoke current token"
6. Actualiza el `.env` con el nuevo token

## Próximos Pasos

Una vez configurado el bot:

1. ✅ Prueba todos los comandos
2. ✅ Configura n8n para automatizaciones avanzadas
3. ✅ Personaliza los mensajes si lo deseas
4. ✅ Agrega más empleados a la lista de autorizados

¡Tu bot de Telegram está listo! 🎉
