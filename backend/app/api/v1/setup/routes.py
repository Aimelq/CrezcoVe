"""
Endpoint para registro inicial del primer usuario (solo disponible si no hay usuarios).
"""
from flask import Blueprint, request, jsonify
from app.core.extensions import db
from app.models import Usuario
from app.core.decorators import validate_request
from marshmallow import Schema, fields, validate

bp = Blueprint('setup', __name__, url_prefix='/api/setup')

class SetupSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    nombre_completo = fields.Str(required=True, validate=validate.Length(min=3))

@bp.route('/status', methods=['GET'])
def check_setup_status():
    """Verifica si el sistema necesita configuración inicial."""
    usuarios_count = Usuario.query.count()
    
    return jsonify({
        'necesita_setup': usuarios_count == 0,
        'mensaje': 'Sistema listo para configuración inicial' if usuarios_count == 0 else 'Sistema ya configurado'
    }), 200

@bp.route('/initial-admin', methods=['POST'])
@validate_request(SetupSchema)
def create_initial_admin():
    """Crea el primer usuario administrador del sistema."""
    
    # Verificar que no existan usuarios
    if Usuario.query.count() > 0:
        return jsonify({
            'error': 'El sistema ya ha sido configurado. Use la página de login.'
        }), 403
    
    data = request.get_json()
    
    # Verificar que el email no exista (por si acaso)
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Este email ya está registrado'}), 400
    
    # Crear el primer administrador
    import secrets
    admin = Usuario(
        email=data['email'],
        nombre_completo=data['nombre_completo'],
        rol='DUENO',  # El primer usuario siempre es dueño
        esta_activo=True,
        email_verificado=False,
        token_verificacion=secrets.token_urlsafe(32)
    )
    admin.establecer_password(data['password'])
    
    db.session.add(admin)
    db.session.commit()
    
    # DISPARAR WEBHOOK N8N
    from app.services.servicio_n8n import servicio_n8n
    servicio_n8n.enviar_verificacion_admin(admin, admin.token_verificacion)
    
    return jsonify({
        'mensaje': '¡Sistema configurado exitosamente! Ya puedes iniciar sesión.',
        'usuario': {
            'id': admin.id,
            'email': admin.email,
            'nombre_completo': admin.nombre_completo,
            'rol': admin.rol
        }
    }), 201
