"""
Endpoints de Autenticación.
Maneja registro, login, logout y refresh de tokens.
"""
from flask import request
from marshmallow import Schema, fields as ma_fields, validate
from app.core.decorators import validate_request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from app.core.extensions import db, redis_client
from app.models import Usuario
from app.middleware.audit_middleware import registrar_accion_auditoria

# Crear namespace
auth_ns = Namespace('auth', description='Operaciones de autenticación')

# Modelos para documentación Swagger
modelo_registro = auth_ns.model('Registro', {
    'nombre_completo': fields.String(required=True, description='Nombre completo del usuario'),
    'email': fields.String(required=True, description='Correo electrónico'),
    'password': fields.String(required=True, description='Contraseña'),
    'telefono': fields.String(description='Teléfono'),
    'rol': fields.String(description='Rol del usuario (DUENO, EMPLEADO)', default='EMPLEADO')
})

modelo_login = auth_ns.model('Login', {
    'email': fields.String(required=True, description='Correo electrónico'),
    'password': fields.String(required=True, description='Contraseña')
})

modelo_respuesta_token = auth_ns.model('RespuestaToken', {
    'access_token': fields.String(description='Token de acceso'),
    'refresh_token': fields.String(description='Token de refresco'),
    'usuario': fields.Raw(description='Información del usuario')
})


@auth_ns.route('/registro')
class Registro(Resource):
    class RegistroSchema(Schema):
        nombre_completo = ma_fields.Str(required=True, validate=validate.Length(min=3))
        email = ma_fields.Email(required=True)
        password = ma_fields.Str(required=True, validate=validate.Length(min=6))
        telefono = ma_fields.Str(required=False, validate=validate.Regexp(r"^[\d\+\-\s\(\)]{7,20}$"))
        rol = ma_fields.Str(required=False, validate=validate.OneOf(['DUENO', 'EMPLEADO']))

    @auth_ns.expect(modelo_registro)
    @validate_request(RegistroSchema)
    @jwt_required(optional=True)
    @auth_ns.expect(modelo_registro)
    @auth_ns.marshal_with(modelo_respuesta_token, code=201)
    def post(self):
        """Registra un nuevo usuario."""
        # Se requiere ser DUENO para registrar empleados, 
        # excepto si no hay usuarios (setup inicial)
        usuario_actual_id = get_jwt_identity()
        hay_usuarios = Usuario.query.first() is not None
        
        if hay_usuarios:
            if not usuario_actual_id:
                auth_ns.abort(401, 'Se requiere autenticación')
            
            usuario_actual = Usuario.query.get(int(usuario_actual_id))
            if not usuario_actual or usuario_actual.rol != 'DUENO':
                auth_ns.abort(403, 'Solo el administrador puede registrar nuevos usuarios')
        
        datos = request.get_json()
        
        # Validar que el email no exista
        if Usuario.query.filter_by(email=datos['email']).first():
            auth_ns.abort(400, 'El email ya está registrado')
        
        # Crear usuario
        usuario = Usuario(
            nombre_completo=datos['nombre_completo'],
            email=datos['email'],
            telefono=datos.get('telefono'),
            rol=datos.get('rol', 'EMPLEADO')
        )
        usuario.establecer_password(datos['password'])
        
        # Si es el primer usuario o rol DUENO, generar token de verificación
        import secrets
        if usuario.rol == 'DUENO':
            usuario.token_verificacion = secrets.token_urlsafe(32)
            usuario.email_verificado = False
        else:
            # Empleados registrados por admin se consideran verificados o no requieren validación de correo para entrar
            usuario.email_verificado = True
            
        db.session.add(usuario)
        db.session.commit()
        
        # DISPARAR WEBHOOKS N8N
        from app.services.servicio_n8n import servicio_n8n
        if usuario.rol == 'DUENO':
            servicio_n8n.enviar_verificacion_admin(usuario, usuario.token_verificacion)
        else:
            servicio_n8n.enviar_bienvenida_usuario(usuario, datos['password'])

        # Registrar en auditoría
        registrar_accion_auditoria(
            accion='CREAR',
            tabla_afectada='usuarios',
            registro_id=usuario.id,
            valores_nuevos=usuario.to_dict()
        )
        
        # Si es DUENO, no devolver tokens aún (debe verificar)
        if usuario.rol == 'DUENO':
            return {
                'mensaje': 'Registro exitoso. Por favor verifica tu correo electrónico.',
                'usuario': usuario.to_dict()
            }, 201

        # Generar tokens para empleados (si el admin los registra)
        access_token = create_access_token(identity=str(usuario.id))
        refresh_token = create_refresh_token(identity=str(usuario.id))
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'usuario': usuario.to_dict()
        }, 201


@auth_ns.route('/login')
class Login(Resource):
    class LoginSchema(Schema):
        email = ma_fields.Email(required=True)
        password = ma_fields.Str(required=True, validate=validate.Length(min=6))

    @auth_ns.expect(modelo_login)
    @validate_request(LoginSchema)
    @auth_ns.marshal_with(modelo_respuesta_token)
    def post(self):
        """Inicia sesión y obtiene tokens."""
        datos = request.get_json()
        
        # Buscar usuario
        usuario = Usuario.query.filter_by(email=datos['email']).first()
        
        if not usuario or not usuario.verificar_password(datos['password']):
            auth_ns.abort(401, 'Credenciales inválidas')
        
        if not usuario.esta_activo:
            auth_ns.abort(403, 'Usuario inactivo')
            
        # NUEVO: Bloquear login de DUENO si no está verificado
        if usuario.rol == 'DUENO' and not usuario.email_verificado:
            # Solo permitir login si es el único usuario y acaba de registrarse? 
            # Mejor bloquear y pedir verificación
            from app.services.servicio_n8n import servicio_n8n
            import secrets
            if not usuario.token_verificacion:
               usuario.token_verificacion = secrets.token_urlsafe(32)
               db.session.commit()
            
            servicio_n8n.enviar_verificacion_admin(usuario, usuario.token_verificacion)
            auth_ns.abort(403, 'Debes verificar tu correo electrónico antes de iniciar sesión. Se ha enviado un nuevo enlace.')
        
        # Generar tokens
        access_token = create_access_token(identity=str(usuario.id))
        refresh_token = create_refresh_token(identity=str(usuario.id))
        
        # Registrar login en auditoría
        registrar_accion_auditoria(
            accion='LOGIN',
            tabla_afectada='usuarios',
            registro_id=usuario.id
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'usuario': usuario.to_dict()
        }


@auth_ns.route('/verificar-email')
class VerificarEmail(Resource):
    @auth_ns.doc(params={'token': 'Token de verificación enviado por email'})
    def get(self):
        """Verifica el email de un usuario mediante un token."""
        token = request.args.get('token')
        if not token:
            auth_ns.abort(400, 'Se requiere un token de verificación')
            
        usuario = Usuario.query.filter_by(token_verificacion=token).first()
        if not usuario:
            auth_ns.abort(404, 'Token inválido o expirado')
            
        usuario.email_verificado = True
        usuario.token_verificacion = None
        db.session.commit()
        
        registrar_accion_auditoria(
            accion='VERIFICACION_EMAIL',
            tabla_afectada='usuarios',
            registro_id=usuario.id
        )
        
        return {'mensaje': 'Email verificado exitosamente. Ya puedes iniciar sesión.'}


@auth_ns.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """Refresca el access token usando el refresh token."""
        usuario_id = get_jwt_identity()
        access_token = create_access_token(identity=str(usuario_id))
        
        return {
            'access_token': access_token
        }


@auth_ns.route('/logout')
class Logout(Resource):
    @jwt_required()
    def post(self):
        """Cierra sesión revocando el token."""
        jti = get_jwt()['jti']
        usuario_id = get_jwt_identity()
        
        # Agregar token a lista de revocados en Redis (expira en 1 hora)
        redis_client.setex(f'token_revocado:{jti}', 3600, 'true')
        
        # Registrar logout
        registrar_accion_auditoria(
            accion='LOGOUT',
            tabla_afectada='usuarios',
            registro_id=usuario_id
        )
        
        return {
            'mensaje': 'Sesión cerrada exitosamente'
        }


@auth_ns.route('/perfil')
class Perfil(Resource):
    @jwt_required()
    def get(self):
        """Obtiene el perfil del usuario actual."""
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(int(usuario_id))
        
        if not usuario:
            auth_ns.abort(404, 'Usuario no encontrado')
        
        return usuario.to_dict()

    @jwt_required()
    @auth_ns.expect(auth_ns.model('ActualizarPerfil', {
        'nombre_completo': fields.String(description='Nombre completo'),
        'email': fields.String(description='Email'),
        'telefono': fields.String(description='Teléfono'),
        'telegram_chat_id': fields.String(description='ID de Chat de Telegram')
    }))
    def put(self):
        """Actualiza el perfil del usuario actual."""
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(int(usuario_id))
        
        if not usuario:
            auth_ns.abort(404, 'Usuario no encontrado')
            
        datos = request.get_json()
        
        if 'email' in datos and datos['email'] != usuario.email:
            if Usuario.query.filter_by(email=datos['email']).first():
                auth_ns.abort(400, 'El email ya está en uso')
        
        for campo in ['nombre_completo', 'email', 'telefono', 'telegram_chat_id']:
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


@auth_ns.route('/cambiar-password')
class CambiarPassword(Resource):
    @jwt_required()
    @auth_ns.expect(auth_ns.model('CambioPassword', {
        'password_actual': fields.String(required=True),
        'password_nuevo': fields.String(required=True)
    }))
    def post(self):
        """Cambia la contraseña del usuario actual."""
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(int(usuario_id))
        
        datos = request.get_json()
        
        if not usuario.verificar_password(datos['password_actual']):
            auth_ns.abort(400, 'La contraseña actual es incorrecta')
            
        usuario.establecer_password(datos['password_nuevo'])
        db.session.commit()
        
        registrar_accion_auditoria(
            accion='CAMBIO_PASSWORD',
            tabla_afectada='usuarios',
            registro_id=usuario.id
        )
        
        return {'mensaje': 'Contraseña actualizada exitosamente'}
