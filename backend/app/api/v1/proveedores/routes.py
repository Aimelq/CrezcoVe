"""
Endpoints de Proveedores.
Maneja CRUD de proveedores y generación de pedidos.
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from marshmallow import Schema, fields as ma_fields, validate
from app.core.decorators import validate_request
from flask_jwt_extended import jwt_required
from app.core.extensions import db
from app.models import Proveedor, Producto
from app.services.prediccion_agotamiento import ServicioPrediccion

# Crear namespace
proveedores_ns = Namespace('proveedores', description='Operaciones de proveedores')

# Modelos para Swagger
modelo_proveedor = proveedores_ns.model('Proveedor', {
    'nombre': fields.String(required=True, description='Nombre del proveedor'),
    'nombre_contacto': fields.String(description='Nombre de contacto'),
    'telefono': fields.String(description='Teléfono'),
    'email': fields.String(description='Email'),
    'direccion': fields.String(description='Dirección'),
    'rif': fields.String(description='RIF (Venezuela)'),
    'terminos_pago': fields.String(description='Términos de pago'),
    'notas': fields.String(description='Notas')
})
class ProveedorSchema(Schema):
    nombre = ma_fields.Str(required=True, validate=validate.Length(min=2))
    nombre_contacto = ma_fields.Str(required=False)
    telefono = ma_fields.Str(required=False, validate=validate.Regexp(r"^[\d\+\-\s\(\)]{7,20}$"))
    email = ma_fields.Email(required=False)
    direccion = ma_fields.Str(required=False)
    rif = ma_fields.Str(required=True, validate=validate.Regexp(r"^[JVG]-\d{8}-\d$", error="Formato de RIF inválido (Ej: J-12345678-9)"))
    terminos_pago = ma_fields.Str(required=False)
    notas = ma_fields.Str(required=False)


@proveedores_ns.route('')
class ListaProveedores(Resource):
    @jwt_required()
    def get(self):
        """Obtiene lista de proveedores."""
        proveedores = Proveedor.query.filter_by(esta_activo=True).all()
        return {
            'proveedores': [p.to_dict() for p in proveedores]
        }
    
    @jwt_required()
    @proveedores_ns.expect(modelo_proveedor)
    @validate_request(ProveedorSchema)
    def post(self):
        """Crea un nuevo proveedor."""
        datos = request.get_json()
        
        # Validar que el RIF no exista
        if Proveedor.query.filter_by(rif=datos.get('rif')).first():
            return {
                'error': 'Error de validación',
                'mensaje': 'El RIF ya está registrado',
                'codigo': 400
            }, 400
            
        proveedor = Proveedor(**datos)
        db.session.add(proveedor)
        db.session.commit()
        
        return proveedor.to_dict(), 201

    


@proveedores_ns.route('/<int:id>')
class DetalleProveedor(Resource):
    @jwt_required()
    def get(self, id):
        """Obtiene detalles de un proveedor."""
        proveedor = Proveedor.query.get(id)
        if not proveedor or not proveedor.esta_activo:
            proveedores_ns.abort(404, 'Proveedor no encontrado')
        
        return proveedor.to_dict()
    
    @jwt_required()
    @proveedores_ns.expect(modelo_proveedor)
    @validate_request(ProveedorSchema)
    def put(self, id):
        """Actualiza un proveedor."""
        proveedor = Proveedor.query.get(id)
        if not proveedor:
            proveedores_ns.abort(404, 'Proveedor no encontrado')
        
        datos = request.get_json()
        
        # Validar RIF si está cambiando
        if 'rif' in datos and datos['rif'] != proveedor.rif:
            if Proveedor.query.filter_by(rif=datos['rif']).first():
                return {
                    'error': 'Error de validación',
                    'mensaje': 'El RIF ya está registrado por otro proveedor',
                    'codigo': 400
                }, 400
                
        # Obtener columnas de la tabla para filtrar
        columnas = Proveedor.__table__.columns.keys()
                
        for campo, valor in datos.items():
            if campo in columnas and campo != 'id':
                setattr(proveedor, campo, valor)
        
        db.session.commit()
        return proveedor.to_dict()


@proveedores_ns.route('/<int:id>/pedido-sugerido')
class PedidoSugerido(Resource):
    @jwt_required()
    def get(self, id):
        """Genera pedido sugerido basado en productos del proveedor que están bajos."""
        proveedor = Proveedor.query.get(id)
        if not proveedor:
            proveedores_ns.abort(404, 'Proveedor no encontrado')
        
        # Obtener productos del proveedor
        productos_proveedor = proveedor.productos
        
        productos_a_pedir = []
        for producto in productos_proveedor:
            if producto.esta_bajo_stock:
                # Obtener predicción
                try:
                    prediccion = ServicioPrediccion.predecir_agotamiento(producto.id)
                    cantidad_sugerida = prediccion.get('cantidad_sugerida_pedido', producto.stock_minimo * 2)
                except:
                    cantidad_sugerida = producto.stock_minimo * 2
                
                productos_a_pedir.append({
                    'producto_id': producto.id,
                    'codigo_sku': producto.codigo_sku,
                    'nombre': producto.nombre,
                    'stock_actual': producto.cantidad_actual,
                    'stock_minimo': producto.stock_minimo,
                    'cantidad_sugerida': round(cantidad_sugerida, 2),
                    'ultimo_costo': float(producto.ultimo_costo_compra) if producto.ultimo_costo_compra else float(producto.costo_promedio),
                    'costo_estimado': round(cantidad_sugerida * float(producto.ultimo_costo_compra or producto.costo_promedio), 2)
                })
        
        costo_total_estimado = sum(p['costo_estimado'] for p in productos_a_pedir)
        
        return {
            'proveedor_id': id,
            'proveedor_nombre': proveedor.nombre,
            'productos_a_pedir': productos_a_pedir,
            'total_productos': len(productos_a_pedir),
            'costo_total_estimado': round(costo_total_estimado, 2)
        }
