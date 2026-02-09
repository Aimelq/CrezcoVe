"""
Endpoints para la gestión de Lotes.
Permite visualizar el desglose de inventario por lotes y sus vencimientos.
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from app.core.extensions import db
from app.models import LoteProducto, Producto

lotes_ns = Namespace('lotes', description='Gestión de lotes y trazabilidad')

# Modelos para Swagger
modelo_lote = lotes_ns.model('Lote', {
    'id': fields.Integer(readOnly=True),
    'producto_id': fields.Integer(required=True),
    'producto_nombre': fields.String(attribute='producto.nombre'),
    'numero_lote': fields.String(required=True),
    'fecha_vencimiento': fields.Date(),
    'cantidad_inicial': fields.Float(),
    'cantidad_actual': fields.Float(),
    'costo_lote': fields.Float(),
    'proveedor_nombre': fields.String(attribute='proveedor.nombre'),
    'creado_en': fields.DateTime(),
    'dias_hasta_vencimiento': fields.Integer()
})

@lotes_ns.route('/')
class ListaLotes(Resource):
    @jwt_required()
    @lotes_ns.marshal_list_with(modelo_lote)
    def get(self):
        """Lista todos los lotes activos con existencias de productos activos."""
        return LoteProducto.query.join(Producto).filter(
            LoteProducto.cantidad_actual > 0,
            LoteProducto.esta_activo == True,
            Producto.esta_activo == True
        ).order_by(LoteProducto.fecha_vencimiento.asc().nullslast()).all()

@lotes_ns.route('/producto/<int:producto_id>')
class LotesPorProducto(Resource):
    @jwt_required()
    @lotes_ns.marshal_list_with(modelo_lote)
    def get(self, producto_id):
        """Obtiene los lotes de un producto específico si está activo."""
        return LoteProducto.query.filter_by(
            producto_id=producto_id,
            esta_activo=True
        ).filter(LoteProducto.cantidad_actual > 0).order_by(LoteProducto.fecha_vencimiento.asc().nullslast()).all()
