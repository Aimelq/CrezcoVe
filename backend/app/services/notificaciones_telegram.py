"""
Servicio de notificaciones de Telegram.
Envía alertas y notificaciones a los usuarios.
"""
import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class ServicioNotificacionesTelegram:
    """Servicio para enviar notificaciones vía Telegram."""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id_dueno = os.getenv('TELEGRAM_CHAT_ID_DUENO')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def enviar_mensaje(self, mensaje: str, chat_id: Optional[str] = None, parse_mode: str = 'Markdown'):
        """
        Envía un mensaje de Telegram.
        
        Args:
            mensaje: Texto del mensaje
            chat_id: ID del chat (opcional, usa el del dueño por defecto)
            parse_mode: Formato del mensaje (Markdown o HTML)
        """
        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN no configurado")
            return False
        
        chat_id = chat_id or self.chat_id_dueno
        
        if not chat_id:
            logger.warning("No hay chat_id configurado")
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': mensaje,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Mensaje enviado a Telegram: {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar mensaje de Telegram: {e}")
            return False
    
    def notificar_stock_bajo(self, producto_nombre: str, stock_actual: float, stock_minimo: float):
        """Notifica cuando un producto tiene stock bajo."""
        mensaje = f"""
⚠️ *ALERTA: Stock Bajo*

Producto: *{producto_nombre}*
Stock Actual: {stock_actual}
Stock Mínimo: {stock_minimo}

🔔 Se requiere reposición urgente.
"""
        self.enviar_mensaje(mensaje)
    
    def notificar_producto_agotado(self, producto_nombre: str, dias_estimados: int):
        """Notifica cuando un producto está por agotarse."""
        mensaje = f"""
🔴 *ALERTA CRÍTICA: Producto por Agotarse*

Producto: *{producto_nombre}*
⏰ Tiempo estimado: {dias_estimados} días

🚨 Realizar pedido inmediatamente.
"""
        self.enviar_mensaje(mensaje)
    
    def notificar_discrepancia_auditoria(self, producto_nombre: str, cantidad_sistema: float, cantidad_fisica: float, diferencia_porcentaje: float):
        """Notifica discrepancias en auditoría."""
        mensaje = f"""
🚨 *ALERTA: Discrepancia en Auditoría*

Producto: *{producto_nombre}*
Sistema: {cantidad_sistema}
Físico: {cantidad_fisica}
Diferencia: {diferencia_porcentaje:.1f}%

⚠️ Revisar posible robo o error de registro.
"""
        self.enviar_mensaje(mensaje)
    
    def notificar_inflacion_detectada(self, producto_nombre: str, costo_anterior: float, costo_nuevo: float, precio_sugerido: float):
        """Notifica cuando se detecta inflación."""
        variacion = ((costo_nuevo - costo_anterior) / costo_anterior) * 100
        
        mensaje = f"""
📈 *Inflación Detectada*

Producto: *{producto_nombre}*
Costo Anterior: ${costo_anterior:.2f}
Costo Nuevo: ${costo_nuevo:.2f}
Variación: +{variacion:.1f}%

💡 Precio sugerido: ${precio_sugerido:.2f}
"""
        self.enviar_mensaje(mensaje)
    
    def enviar_reporte_diario(self, total_ventas: float, ganancia: float, productos_criticos: int, alertas_activas: int):
        """Envía reporte diario de cierre."""
        mensaje = f"""
📊 *Reporte Diario de Cierre*

💰 *Ventas del Día:* ${total_ventas:.2f}
✅ *Ganancia:* ${ganancia:.2f}

⚠️ *Productos Críticos:* {productos_criticos}
🔔 *Alertas Activas:* {alertas_activas}

_Reporte generado automáticamente_
"""
        self.enviar_mensaje(mensaje)


# Instancia global del servicio
servicio_telegram = ServicioNotificacionesTelegram()
