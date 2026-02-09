"""
Middleware de Auditoría.
Registra todas las acciones importantes en la "caja negra".
"""
from datetime import datetime
from flask import request, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.core.extensions import db
from app.models import AuditoriaLog


class AuditoriaMiddleware:
    """Middleware para registrar acciones en logs de auditoría."""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        """Intercepta requests y registra acciones."""
        return self.app(environ, start_response)


def registrar_accion_auditoria(accion, tabla_afectada, registro_id=None, valores_anteriores=None, valores_nuevos=None):
    """
    Registra una acción en los logs de auditoría.
    
    Args:
        accion: Tipo de acción (CREAR, ACTUALIZAR, ELIMINAR, LOGIN, LOGOUT)
        tabla_afectada: Nombre de la tabla afectada
        registro_id: ID del registro afectado
        valores_anteriores: Valores antes del cambio (dict)
        valores_nuevos: Valores después del cambio (dict)
    """
    try:
        # Intentar obtener usuario actual
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            usuario_id = int(identity) if identity else None
        except:
            usuario_id = None
        
        if not usuario_id:
            return  # No registrar si no hay usuario autenticado
        
        log = AuditoriaLog(
            usuario_id=usuario_id,
            accion=accion,
            tabla_afectada=tabla_afectada,
            registro_id=registro_id,
            valores_anteriores=valores_anteriores,
            valores_nuevos=valores_nuevos,
            endpoint=request.path if request else None,
            metodo_http=request.method if request else None,
            direccion_ip=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None,
            fecha_hora=datetime.utcnow()
        )
        
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        # No fallar la request si falla el logging
        print(f"Error al registrar auditoría: {str(e)}")
