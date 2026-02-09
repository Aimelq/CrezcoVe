"""
Endpoints de Alertas.
Maneja la visualización y resolución de alertas del sistema.
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.core.extensions import db
from app.models import Alerta, Usuario
from app.middleware.audit_middleware import registrar_accion_auditoria

# Crear namespace
alertas_ns = Namespace('alertas', description='Operaciones de alertas y notificaciones')

# Modelo para Swagger
modelo_alerta = alertas_ns.model('Alerta', {
    'id': fields.Integer(readOnly=True),
    'tipo_alerta': fields.String(description='Tipo de alerta'),
    'titulo': fields.String(description='Título'),
    'mensaje': fields.String(description='Mensaje detallado'),
    'prioridad': fields.String(description='Prioridad (BAJA, MEDIA, ALTA, CRITICA)'),
    'esta_resuelta': fields.Boolean(description='Estado de resolución'),
    'creado_en': fields.String(description='Fecha de creación'),
    'producto_id': fields.Integer(description='ID del producto relacionado')
})


@alertas_ns.route('')
class ListaAlertas(Resource):
    @alertas_ns.marshal_list_with(modelo_alerta)
    @jwt_required()
    def get(self):
        """Obtiene lista de alertas activas (no resueltas)."""
        solo_activas = request.args.get('solo_activas', 'true').lower() == 'true'
        
        query = Alerta.query
        if solo_activas:
            query = query.filter_by(esta_resuelta=False)
            
        alertas = query.order_by(db.desc(Alerta.creado_en)).all()
        return alertas


@alertas_ns.route('/<int:id>/resolver')
class ResolverAlerta(Resource):
    @jwt_required()
    def post(self, id):
        """Marca una alerta como resuelta."""
        usuario_id = int(get_jwt_identity())
        alerta = Alerta.query.get(id)
        
        if not alerta:
            alertas_ns.abort(404, 'Alerta no encontrada')
            
        datos = request.get_json() or {}
        notas = datos.get('notas', 'Resuelta desde la interfaz')
        
        alerta.marcar_como_resuelta(usuario_id, notas)
        db.session.commit()
        
        registrar_accion_auditoria(
            accion='ACTUALIZAR',
            tabla_afectada='alertas',
            registro_id=alerta.id,
            valores_nuevos={'esta_resuelta': True}
        )
        
        return {'mensaje': 'Alerta resuelta exitosamente'}
