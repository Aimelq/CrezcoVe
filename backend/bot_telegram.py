"""
Bot de Telegram para el Sistema de Inventario.
Permite consultas y recibe notificaciones.
"""
import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Producto, MovimientoInventario, Usuario, Alerta
from app.services.prediccion_agotamiento import ServicioPrediccion

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuración de base de datos
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://usuario_inventario:password@localhost:5432/inventario_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# IDs de chat autorizados
CHAT_ID_DUENO = os.getenv('TELEGRAM_CHAT_ID_DUENO')
CHAT_IDS_EMPLEADOS = os.getenv('TELEGRAM_CHAT_IDS_EMPLEADOS', '').split(',')
CHAT_IDS_AUTORIZADOS = [CHAT_ID_DUENO] + [id for id in CHAT_IDS_EMPLEADOS if id]


def verificar_autorizacion(chat_id: str) -> bool:
    """Verifica si el chat_id está autorizado."""
    return str(chat_id) in CHAT_IDS_AUTORIZADOS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Mensaje de bienvenida."""
    chat_id = str(update.effective_chat.id)
    
    mensaje = f"""
🏪 *Sistema de Inventario Inteligente*

¡Bienvenido! Tu Chat ID es: `{chat_id}`

*Comandos disponibles:*
/stock [sku] - Consultar stock (ej: /stock PROD-1)
/stockbajo - Ver productos con stock bajo
/ventashoy - Resumen de ventas del día
/balance - Balance del inventario
/criticos - Productos en estado crítico
/proveedores - Listar proveedores
/help - Ver esta ayuda

💡 *Tip:* Los comandos funcionan con o sin guion bajo (ej: /ventashoy o /ventas_hoy).
"""
    
    await update.message.reply_text(mensaje, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help - Ayuda."""
    await start(update, context)


async def stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stock - Consultar stock de un producto."""
    chat_id = str(update.effective_chat.id)
    
    if not verificar_autorizacion(chat_id):
        await update.message.reply_text("❌ No estás autorizado para usar este bot.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📦 Uso: /stock [codigo_sku]\nEjemplo: /stock PROD-001"
        )
        return
    
    codigo_sku = context.args[0].upper()
    
    db = SessionLocal()
    try:
        producto = db.query(Producto).filter_by(
            codigo_sku=codigo_sku,
            esta_activo=True
        ).first()
        
        if not producto:
            await update.message.reply_text(f"❌ Producto '{codigo_sku}' no encontrado.")
            return
        
        # Obtener predicción
        try:
            prediccion = ServicioPrediccion.predecir_agotamiento(producto.id)
            dias_hasta_agotar = prediccion.get('dias_hasta_agotar', 'N/A')
            nivel_urgencia = prediccion.get('nivel_urgencia', 'NORMAL')
        except:
            dias_hasta_agotar = 'N/A'
            nivel_urgencia = 'NORMAL'
        
        # Emoji según urgencia
        emoji_urgencia = {
            'CRITICO': '🔴',
            'URGENTE': '🟠',
            'ATENCION': '🟡',
            'NORMAL': '🟢',
            'SIN_DATOS': '⚪'
        }.get(nivel_urgencia, '⚪')
        
        mensaje = f"""
📦 *{producto.nombre}*
SKU: `{producto.codigo_sku}`

*Stock Actual:* {producto.cantidad_actual} {producto.unidad_medida}
*Stock Mínimo:* {producto.stock_minimo}
*Precio Venta:* ${producto.precio_venta:.2f}
*Costo Promedio:* ${float(producto.costo_promedio):.2f}
*Margen:* {producto.margen_actual:.1f}%

{emoji_urgencia} *Estado:* {nivel_urgencia}
⏰ *Días hasta agotar:* {dias_hasta_agotar if isinstance(dias_hasta_agotar, str) else f'{dias_hasta_agotar:.1f}'}

*Valor en Inventario:* ${producto.valor_inventario:.2f}
"""
        
        if producto.esta_bajo_stock:
            mensaje += "\n⚠️ *ALERTA: Stock bajo*"
        
        await update.message.reply_text(mensaje, parse_mode='Markdown')
        
    finally:
        db.close()


async def stock_bajo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stock_bajo - Ver productos con stock bajo."""
    chat_id = str(update.effective_chat.id)
    
    if not verificar_autorizacion(chat_id):
        await update.message.reply_text("❌ No estás autorizado para usar este bot.")
        return
    
    db = SessionLocal()
    try:
        productos = db.query(Producto).filter(
            Producto.esta_activo == True,
            Producto.cantidad_actual <= Producto.stock_minimo
        ).all()
        
        if not productos:
            await update.message.reply_text("✅ No hay productos con stock bajo.")
            return
        
        mensaje = f"⚠️ *Productos con Stock Bajo* ({len(productos)})\n\n"
        
        for p in productos[:10]:  # Limitar a 10
            mensaje += f"• *{p.nombre}*\n"
            mensaje += f"  SKU: `{p.codigo_sku}`\n"
            mensaje += f"  Stock: {p.cantidad_actual}/{p.stock_minimo}\n\n"
        
        if len(productos) > 10:
            mensaje += f"\n_... y {len(productos) - 10} más_"
        
        await update.message.reply_text(mensaje, parse_mode='Markdown')
        
    finally:
        db.close()


async def ventas_hoy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ventas_hoy - Resumen de ventas del día."""
    chat_id = str(update.effective_chat.id)
    
    if not verificar_autorizacion(chat_id):
        await update.message.reply_text("❌ No estás autorizado para usar este bot.")
        return
    
    db = SessionLocal()
    try:
        from datetime import timedelta
        ahora_utc = datetime.utcnow()
        # Ajuste a hora local (VET -4)
        ahora_vet = ahora_utc - timedelta(hours=4)
        inicio_hoy_vet = ahora_vet.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Inicio hoy en UTC para comparar con la BD
        inicio_hoy_utc = inicio_hoy_vet + timedelta(hours=4)
        
        ventas = db.query(MovimientoInventario).filter(
            MovimientoInventario.tipo_movimiento == 'VENTA',
            MovimientoInventario.fecha_movimiento >= inicio_hoy_utc
        ).all()
        
        if not ventas:
            await update.message.reply_text("📊 No hay ventas registradas hoy.")
            return
        
        total_ventas = sum(float(v.precio_total) for v in ventas if v.precio_total)
        total_costo = sum(float(v.costo_total) for v in ventas if v.costo_total)
        ganancia = total_ventas - total_costo
        cantidad_ventas = len(ventas)
        
        mensaje = f"""
💰 *Resumen de Ventas - Hoy*
_{ahora_vet.strftime('%d/%m/%Y %I:%M %p')}_

*Total Ventas:* ${total_ventas:.2f}
*Costo Total:* ${total_costo:.2f}
*Ganancia:* ${ganancia:.2f}
*Margen:* {(ganancia/total_ventas*100) if total_ventas > 0 else 0:.1f}%

*Cantidad de Ventas:* {cantidad_ventas}
*Promedio por Venta:* ${total_ventas/cantidad_ventas:.2f}
"""
        
        await update.message.reply_text(mensaje, parse_mode='Markdown')
        
    finally:
        db.close()


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /balance - Balance del inventario."""
    chat_id = str(update.effective_chat.id)
    
    if not verificar_autorizacion(chat_id):
        await update.message.reply_text("❌ No estás autorizado para usar este bot.")
        return
    
    db = SessionLocal()
    try:
        productos = db.query(Producto).filter_by(esta_activo=True).all()
        
        valor_total = sum(p.valor_inventario for p in productos)
        productos_bajo_stock = sum(1 for p in productos if p.esta_bajo_stock)
        
        mensaje = f"""
📊 *Balance del Inventario*

*Total Productos:* {len(productos)}
*Valor Total:* ${valor_total:.2f}
*Productos con Stock Bajo:* {productos_bajo_stock}

*Porcentaje Stock Bajo:* {(productos_bajo_stock/len(productos)*100) if productos else 0:.1f}%
"""
        
        await update.message.reply_text(mensaje, parse_mode='Markdown')
        
    finally:
        db.close()


async def criticos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /criticos - Productos críticos."""
    chat_id = str(update.effective_chat.id)
    
    if not verificar_autorizacion(chat_id):
        await update.message.reply_text("❌ No estás autorizado para usar este bot.")
        return
    
    try:
        productos_criticos = ServicioPrediccion.obtener_productos_criticos(limite=5)
        
        if not productos_criticos:
            await update.message.reply_text("✅ No hay productos críticos.")
            return
        
        mensaje = f"🔴 *Productos Críticos* ({len(productos_criticos)})\n\n"
        
        for p in productos_criticos:
            emoji = {
                'CRITICO': '🔴',
                'URGENTE': '🟠',
                'ATENCION': '🟡'
            }.get(p.get('nivel_urgencia', 'ATENCION'), '🟡')
            
            mensaje += f"{emoji} *{p['producto_nombre']}*\n"
            mensaje += f"  Stock: {p['stock_actual']}/{p['stock_minimo']}\n"
            
            if p.get('dias_hasta_agotar'):
                mensaje += f"  ⏰ Se agota en {p['dias_hasta_agotar']:.0f} días\n"
            
            mensaje += "\n"
        
        await update.message.reply_text(mensaje, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error en criticos_command: {e}")
        await update.message.reply_text("❌ Error al obtener productos críticos.")


async def proveedores_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /proveedores - Listar proveedores."""
    chat_id = str(update.effective_chat.id)
    
    if not verificar_autorizacion(chat_id):
        await update.message.reply_text("❌ No estás autorizado para usar este bot.")
        return
    
    db = SessionLocal()
    try:
        from app.models import Proveedor
        
        proveedores = db.query(Proveedor).filter_by(esta_activo=True).all()
        
        if not proveedores:
            await update.message.reply_text("📋 No hay proveedores registrados.")
            return
        
        mensaje = f"👥 *Proveedores* ({len(proveedores)})\n\n"
        
        for prov in proveedores[:10]:
            mensaje += f"• *{prov.nombre}*\n"
            if prov.telefono:
                mensaje += f"  📞 {prov.telefono}\n"
            if prov.email:
                mensaje += f"  📧 {prov.email}\n"
            mensaje += "\n"
        
        if len(proveedores) > 10:
            mensaje += f"\n_... y {len(proveedores) - 10} más_"
        
        await update.message.reply_text(mensaje, parse_mode='Markdown')
        
    finally:
        db.close()


def main():
    """Función principal del bot."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN no configurado")
        return
    
    # Crear aplicación
    application = Application.builder().token(token).build()
    
    # Registrar comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stock", stock_command))
    application.add_handler(CommandHandler("stock_bajo", stock_bajo_command))
    application.add_handler(CommandHandler("stockbajo", stock_bajo_command))
    application.add_handler(CommandHandler("ventas_hoy", ventas_hoy_command))
    application.add_handler(CommandHandler("ventashoy", ventas_hoy_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("criticos", criticos_command))
    application.add_handler(CommandHandler("proveedores", proveedores_command))
    
    # Iniciar bot
    logger.info("Bot de Telegram iniciado")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
