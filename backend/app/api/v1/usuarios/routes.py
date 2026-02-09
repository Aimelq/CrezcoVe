"""
Endpoints de Gestión de Usuarios.
Permite a los administradores gestionar empleados.
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.core.extensions import db
from app.models import Usuario
from app.middleware.audit_middleware import registrar_accion_auditoria

# Crear namespace
usuarios_ns = Namespace('usuarios', description='Operaciones de gestión de usuarios (Admin)')

# Modelo para Swagger
modelo_usuario_admin = usuarios_ns.model('UsuarioAdmin', {
    'id': fields.Integer(readOnly=True),
    'nombre_completo': fields.String(required=True),
    'email': fields.String(required=True),
    'rol': fields.String(required=True),
    'esta_activo': fields.Boolean(),
    'telefono': fields.String(),
    'telegram_chat_id': fields.String()
})


def requerir_admin(fn):
    """Decorador simple para requerir rol DUENO."""
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        usuario_id = int(identity) if identity else None
        usuario = Usuario.query.get(usuario_id)
        if not usuario or usuario.rol != 'DUENO':
            usuarios_ns.abort(403, 'Se requieren privilegios de administrador')
        return fn(*args, **kwargs)
    return wrapper


@usuarios_ns.route('')
class ListaUsuarios(Resource):
    @jwt_required()
    @requerir_admin
    @usuarios_ns.marshal_list_with(modelo_usuario_admin)
    def get(self):
        """Lista todos los usuarios (solo Admin)."""
        return Usuario.query.all()


@usuarios_ns.route('/<int:id>')
class DetalleUsuario(Resource):
    @jwt_required()
    @requerir_admin
    @usuarios_ns.marshal_with(modelo_usuario_admin)
    def get(self, id):
        """Obtiene detalles de un usuario."""
        usuario = Usuario.query.get(id)
        if not usuario:
            usuarios_ns.abort(404, 'Usuario no encontrado')
        return usuario

    @jwt_required()
    @requerir_admin
    def put(self, id):
        """Actualiza un usuario."""
        usuario = Usuario.query.get(id)
        if not usuario:
            usuarios_ns.abort(404, 'Usuario no encontrado')
            
        datos = request.get_json()
        
        for campo in ['nombre_completo', 'rol', 'esta_activo', 'telefono', 'telegram_chat_id']:
            if campo in datos:
                setattr(usuario, campo, datos[campo])
                
        db.session.commit()
        
        registrar_accion_auditoria(
            accion='ACTUALIZAR',
            tabla_afectada='usuarios',
            registro_id=usuario.id,
            valores_nuevos=usuario.to_dict()
        )
        
        return usuario.to_dict()

    @jwt_required()
    @requerir_admin
    def delete(self, id):
        """Desactiva un usuario (soft delete)."""
        usuario = Usuario.query.get(id)
        if not usuario:
            usuarios_ns.abort(404, 'Usuario no encontrado')
            
        if usuario.rol == 'DUENO':
            usuarios_ns.abort(400, 'No se puede eliminar al administrador principal')
            
        usuario.esta_activo = False
        db.session.commit()
        
        registrar_accion_auditoria(
            accion='DESACTIVAR',
            tabla_afectada='usuarios',
            registro_id=usuario.id
        )
        
        return {'mensaje': 'Usuario desactivado exitosamente'}
