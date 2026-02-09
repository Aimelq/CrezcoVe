# Bot de Telegram - Sistema de Inventario

Bot de Telegram para consultas y notificaciones del inventario.

## Configuración

### 1. Crear el Bot

1. Habla con [@BotFather](https://t.me/BotFather) en Telegram
2. Envía `/newbot`
3. Sigue las instrucciones y elige un nombre
4. Copia el token que te proporciona

### 2. Obtener tu Chat ID

1. Habla con [@userinfobot](https://t.me/userinfobot) en Telegram
2. El bot te enviará tu Chat ID
3. Copia el número

### 3. Configurar Variables de Entorno

Edita el archivo `.env`:

```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID_DUENO=tu_chat_id_aqui
TELEGRAM_CHAT_IDS_EMPLEADOS=chat_id1,chat_id2
```

## Comandos Disponibles

### Consultas

- `/start` - Mensaje de bienvenida y ayuda
- `/help` - Ver lista de comandos
- `/stock [codigo]` - Consultar stock de un producto
- `/stock_bajo` - Ver productos con stock bajo
- `/ventas_hoy` - Resumen de ventas del día
- `/balance` - Balance del inventario
- `/criticos` - Productos críticos
- `/proveedores` - Listar proveedores

### Ejemplos

```
/stock PROD-001
/stock_bajo
/ventas_hoy
```

## Notificaciones Automáticas

El bot enviará notificaciones automáticas para:

- ⚠️ **Stock Bajo**: Cuando un producto alcanza el stock mínimo
- 🔴 **Producto por Agotarse**: Predicción de agotamiento
- 🚨 **Discrepancia en Auditoría**: Diferencias detectadas
- 📈 **Inflación Detectada**: Aumento de costos
- 📊 **Reporte Diario**: Resumen al final del día

## Ejecutar el Bot

### Con Docker

```bash
docker-compose up -d telegram_bot
```

### Localmente

```bash
cd backend
python bot_telegram.py
```

## Logs

Ver logs del bot:

```bash
docker-compose logs -f telegram_bot
```

## Seguridad

- Solo los Chat IDs configurados pueden usar el bot
- Todos los comandos requieren autorización
- Las notificaciones solo se envían al dueño

## Troubleshooting

### El bot no responde

1. Verifica que el token sea correcto
2. Asegúrate de que el bot esté corriendo
3. Revisa los logs para errores

### No recibo notificaciones

1. Verifica que tu Chat ID esté en `TELEGRAM_CHAT_ID_DUENO`
2. Asegúrate de haber iniciado una conversación con el bot (`/start`)
3. Revisa que el bot tenga acceso a la base de datos
