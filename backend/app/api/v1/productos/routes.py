"""
Endpoints de Productos.
Maneja CRUD de productos y operaciones relacionadas.
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.core.extensions import db
from app.models import Producto, Categoria, Usuario
from app.services.prediccion_agotamiento import ServicioPrediccion
from app.services.servicio_alertas import ServicioAlertas
from app.middleware.audit_middleware import registrar_accion_auditoria

# Crear namespace
productos_ns = Namespace('productos', description='Operaciones de productos')

# Modelos para Swagger
modelo_producto = productos_ns.model('Producto', {
    'codigo_sku': fields.String(required=True, description='Código SKU único'),
    'nombre': fields.String(required=True, description='Nombre del producto'),
    'descripcion': fields.String(description='Descripción'),
    'categoria_id': fields.Integer(description='ID de categoría'),
    'unidad_medida': fields.String(description='Unidad de medida', default='UNIDAD'),
    'cantidad_actual': fields.Float(description='Cantidad en stock'),
    'stock_minimo': fields.Float(required=True, description='Stock mínimo'),
    'stock_maximo': fields.Float(description='Stock máximo'),
    'costo_promedio': fields.Float(description='Costo promedio'),
    'precio_venta': fields.Float(required=True, description='Precio de venta'),
    'margen_deseado': fields.Float(description='Margen deseado (%)', default=30),
    'tiene_vencimiento': fields.Boolean(description='Tiene fecha de vencimiento'),
    'imagen_url': fields.String(description='URL de imagen'),
    'notas': fields.String(description='Notas adicionales'),
    'producto_padre_id': fields.Integer(description='ID del producto bulto/caja'),
    'factor_conversion': fields.Float(description='Factor de conversión (ej: cuántos hay en una caja)', default=1.0)
})


@productos_ns.route('')
class ListaProductos(Resource):
    @jwt_required()
    def get(self):
        """Obtiene lista de productos con filtros opcionales."""
        # Parámetros de query
        buscar = request.args.get('buscar', '')
        categoria_id = request.args.get('categoria_id', type=int)
        stock_bajo = request.args.get('stock_bajo', 'false').lower() == 'true'
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 20, type=int)
        
        # Query base
        query = Producto.query.filter_by(esta_activo=True)
        
        # Aplicar filtros
        if buscar:
            query = query.filter(
                (Producto.nombre.ilike(f'%{buscar}%')) |
                (Producto.codigo_sku.ilike(f'%{buscar}%'))
            )
        
        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)
        
        if stock_bajo:
            query = query.filter(Producto.cantidad_actual <= Producto.stock_minimo)
        
        # Paginación
        paginacion = query.paginate(page=pagina, per_page=por_pagina, error_out=False)
        
        return {
            'items': [p.to_dict() for p in paginacion.items],
            'total': paginacion.total,
            'pagina': pagina,
            'paginas_totales': paginacion.pages,
            'por_pagina': por_pagina
        }
    
    @jwt_required()
    @productos_ns.expect(modelo_producto)
    def post(self):
        """Crea un nuevo producto."""
        datos = request.get_json()
        
        # Validar que el SKU no exista
        if Producto.query.filter_by(codigo_sku=datos['codigo_sku']).first():
            return {
                'error': 'Error de validación',
                'mensaje': 'El código SKU ya existe',
                'codigo': 400
            }, 400
        
        # Crear producto
        producto = Producto(**datos)
        db.session.add(producto)
        db.session.commit()
        
        # Registrar en auditoría
        registrar_accion_auditoria(
            accion='CREAR',
            tabla_afectada='productos',
            registro_id=producto.id,
            valores_nuevos=producto.to_dict()
        )
        
        return producto.to_dict(), 201


@productos_ns.route('/<int:id>')
class DetalleProducto(Resource):
    @jwt_required()
    def get(self, id):
        """Obtiene detalles de un producto."""
        producto = Producto.query.get(id)
        if not producto or not producto.esta_activo:
            productos_ns.abort(404, 'Producto no encontrado')
        
        return producto.to_dict()
    
    @jwt_required()
    @productos_ns.expect(modelo_producto)
    def put(self, id):
        """Actualiza un producto."""
        producto = Producto.query.get(id)
        if not producto:
            productos_ns.abort(404, 'Producto no encontrado')
        
        datos = request.get_json()
        valores_anteriores = producto.to_dict()
        
        # Obtener columnas de la tabla para filtrar campos no permitidos
        columnas = Producto.__table__.columns.keys()
        
        # Actualizar campos
        for campo, valor in datos.items():
            if campo in columnas and campo != 'id':
                setattr(producto, campo, valor)
        
        db.session.commit()
        
        # Verificar márgenes tras actualización manual
        ServicioAlertas.verificar_y_alertar_margen(producto.id)
        
        # Registrar en auditoría
        registrar_accion_auditoria(
            accion='ACTUALIZAR',
            tabla_afectada='productos',
            registro_id=producto.id,
            valores_anteriores=valores_anteriores,
            valores_nuevos=producto.to_dict()
        )
        
        return producto.to_dict()
    
    @jwt_required()
    def delete(self, id):
        """Elimina un producto (soft delete)."""
        producto = Producto.query.get(id)
        if not producto:
            productos_ns.abort(404, 'Producto no encontrado')
        
        valores_anteriores = producto.to_dict()
        producto.soft_delete()
        
        # Registrar en auditoría
        registrar_accion_auditoria(
            accion='ELIMINAR',
            tabla_afectada='productos',
            registro_id=producto.id,
            valores_anteriores=valores_anteriores
        )
        
        return {'mensaje': 'Producto eliminado exitosamente'}


@productos_ns.route('/<int:id>/prediccion-agotamiento')
class PrediccionAgotamiento(Resource):
    @jwt_required()
    def get(self, id):
        """Obtiene predicción de agotamiento del producto."""
        try:
            prediccion = ServicioPrediccion.predecir_agotamiento(id)
            return prediccion
        except ValueError as e:
            productos_ns.abort(404, str(e))


@productos_ns.route('/<int:id>/historial')
class HistorialProducto(Resource):
    @jwt_required()
    def get(self, id):
        """Obtiene historial de movimientos del producto."""
        producto = Producto.query.get(id)
        if not producto:
            productos_ns.abort(404, 'Producto no encontrado')
        
        limite = request.args.get('limite', 50, type=int)
        
        movimientos = producto.movimientos.order_by(
            db.desc('fecha_movimiento')
        ).limit(limite).all()
        
        return {
            'producto_id': id,
            'producto_nombre': producto.nombre,
            'movimientos': [m.to_dict() for m in movimientos]
        }
