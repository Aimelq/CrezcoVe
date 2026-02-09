import os
import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class ServicioN8N:
    """Servicio para enviar webhooks a n8n."""
    
    @staticmethod
    def _enviar_webhook(endpoint, datos):
        """Método privado para enviar el POST al webhook."""
        url_base = current_app.config.get('N8N_WEBHOOK_URL', 'http://n8n:5678/webhook')
        # Asegurarse de que no termine en / para concatenar
        if url_base.endswith('/'):
            url_base = url_base[:-1]
            
        url = f"{url_base}/{endpoint}"
        
        try:
            response = requests.post(url, json=datos, timeout=10)
            response.raise_for_status()
            logger.info(f"Webhook enviado exitosamente a n8n: {endpoint}")
            return True
        except Exception as e:
            logger.error(f"Error al enviar webhook a n8n ({endpoint}): {str(e)}")
            return False

    @staticmethod
    def enviar_verificacion_admin(usuario, token):
        """Envía webhook para correo de verificación de administrador."""
        datos = {
            'email': usuario.email,
            'nombre': usuario.nombre_completo,
            'token': token,
            'link_verificacion': f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/verificar-email?token={token}",
            'tipo': 'VERIFICACION_ADMIN'
        }
        return ServicioN8N._enviar_webhook('admin-registration', datos)

    @staticmethod
    def enviar_bienvenida_usuario(usuario, password_plano):
        """Envía webhook para correo de bienvenida a nuevo usuario/empleado."""
        datos = {
            'email': usuario.email,
            'nombre': usuario.nombre_completo,
            'password': password_plano,
            'rol': usuario.rol,
            'login_url': f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/login",
            'tipo': 'BIENVENIDA_USUARIO'
        }
        return ServicioN8N._enviar_webhook('new-user-welcome', datos)

servicio_n8n = ServicioN8N()
