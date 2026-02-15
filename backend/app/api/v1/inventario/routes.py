"""
Endpoints de Inventario.
Maneja operaciones de entrada, salida y ajustes de inventario.
"""
from datetime import datetime
from flask import request
from flask_restx import Namespace, Resource, fields
from marshmallow import Schema, fields as ma_fields, validate
from app.core.decorators import validate_request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.core.extensions import db
from app.models import Producto, MovimientoInventario, LoteProducto
from app.services.calculadora_costo import CalculadoraCosto
from app.services.asistente_precios import AsistentePrecios
from app.services.servicio_alertas import ServicioAlertas
from app.services.dinero_dormido import ServicioDineroDormido
from app.services.auditoria_ciega import ServicioAuditoriaCiega
from app.services.tasa_cambio import TasaCambioServicio
from app.middleware.audit_middleware import registrar_accion_auditoria

# Crear namespace
inventario_ns = Namespace('inventario', description='Operaciones de inventario')

# Modelos para Swagger
modelo_ingreso = inventario_ns.model('Ingreso', {
    'producto_id': fields.Integer(required=True, description='ID del producto'),
    'cantidad': fields.Float(required=True, description='Cantidad que ingresa'),
    'costo_unitario': fields.Float(required=True, description='Costo unitario de compra'),
    'proveedor_id': fields.Integer(description='ID del proveedor'),
    'referencia_id': fields.String(description='Número de factura/orden'),
    'notas': fields.String(description='Notas adicionales'),
    'numero_lote': fields.String(description='Número de lote'),
    'fecha_vencimiento': fields.String(description='Fecha de vencimiento (YYYY-MM-DD)')
})


class IngresoSchema(Schema):
    producto_id = ma_fields.Integer(required=True)
    cantidad = ma_fields.Float(required=True, validate=validate.Range(min=0.0001))
    costo_unitario = ma_fields.Float(required=True, validate=validate.Range(min=0))
    proveedor_id = ma_fields.Integer(required=False)
    referencia_id = ma_fields.String(required=False)
    notas = ma_fields.String(required=False)
    numero_lote = ma_fields.String(required=False)
    fecha_vencimiento = ma_fields.Date(required=False)

modelo_salida = inventario_ns.model('Salida', {
    'producto_id': fields.Integer(required=True, description='ID del producto'),
    'cantidad': fields.Float(required=True, description='Cantidad que sale'),
    'precio_unitario': fields.Float(required=True, description='Precio de venta unitario'),
    'referencia_id': fields.String(description='Número de factura'),
    'notas': fields.String(description='Notas adicionales')
})


class SalidaSchema(Schema):
    producto_id = ma_fields.Integer(required=True)
    cantidad = ma_fields.Float(required=True, validate=validate.Range(min=0.0001))
    precio_unitario = ma_fields.Float(required=True, validate=validate.Range(min=0))
    referencia_id = ma_fields.String(required=False)
    notas = ma_fields.String(required=False)

modelo_ajuste = inventario_ns.model('Ajuste', {
    'producto_id': fields.Integer(required=True, description='ID del producto'),
    'cantidad': fields.Float(required=True, description='Cantidad a ajustar (positivo o negativo)'),
    'motivo_ajuste': fields.String(required=True, description='DETERIORADO, VENCIDO, USO_INTERNO, ROBO, OTRO'),
    'notas': fields.String(description='Notas explicativas')
})


class AjusteSchema(Schema):
    producto_id = ma_fields.Integer(required=True)
    cantidad = ma_fields.Float(required=True)
    motivo_ajuste = ma_fields.String(required=True, validate=validate.Length(min=3))
    notas = ma_fields.String(required=False)

modelo_item_venta = inventario_ns.model('ItemVenta', {
    'producto_id': fields.Integer(required=True, description='ID del producto'),
    'cantidad': fields.Float(required=True, description='Cantidad que sale'),
    'precio_unitario': fields.Float(required=True, description='Precio de venta unitario')
})

modelo_venta_multiple = inventario_ns.model('VentaMultiple', {
    'items': fields.List(fields.Nested(modelo_item_venta), required=True, description='Lista de productos a vender'),
    'referencia_id': fields.String(description='Número de factura común'),
    'notas': fields.String(description='Notas adicionales para toda la transacción')
})


class ItemVentaSchema(Schema):
    producto_id = ma_fields.Integer(required=True)
    cantidad = ma_fields.Float(required=True, validate=validate.Range(min=0.0001))
    precio_unitario = ma_fields.Float(required=True, validate=validate.Range(min=0))


class VentaMultipleSchema(Schema):
    items = ma_fields.List(ma_fields.Nested(ItemVentaSchema), required=True)
    referencia_id = ma_fields.String(required=False)
    notas = ma_fields.String(required=False)

modelo_tasa = inventario_ns.model('TasaCambio', {
    'tasa': fields.Float(required=True, description='Nueva tasa del dólar BCV')
})


@inventario_ns.route('/ingreso')
class IngresoInventario(Resource):
    @jwt_required()
    @inventario_ns.expect(modelo_ingreso)
    @validate_request(IngresoSchema)
    def post(self):
        """Registra ingreso de mercancía (compra)."""
        datos = request.get_json()
        usuario_id = int(get_jwt_identity())
        
        producto = Producto.query.get(datos['producto_id'])
        if not producto:
            inventario_ns.abort(404, 'Producto no encontrado')
            
        # Validar vencimiento para perecederos
        if producto.tiene_vencimiento:
            if not datos.get('fecha_vencimiento'):
                inventario_ns.abort(400, f'El producto "{producto.nombre}" es perecedero y requiere fecha de vencimiento.')
            
            # Validar que no esté ya vencido (opcional, pero recomendado)
            fecha_venc = datetime.strptime(datos['fecha_vencimiento'], '%Y-%m-%d').date()
            if fecha_venc < datetime.now().date():
                inventario_ns.abort(400, 'No se puede registrar ingreso de producto ya vencido.')
        
        # Calcular nuevo costo promedio
        resultado_costo = CalculadoraCosto.calcular_nuevo_costo_promedio(
            datos['producto_id'],
            datos['cantidad'],
            datos['costo_unitario']
        )
        
        # Analizar impacto en precio
        analisis_precio = AsistentePrecios.analizar_impacto_costo(
            datos['producto_id'],
            datos['costo_unitario']
        )
        
        # Actualizar producto
        cantidad_anterior = producto.cantidad_actual
        CalculadoraCosto.actualizar_costo_producto(
            datos['producto_id'],
            datos['cantidad'],
            datos['costo_unitario']
        )
        
        # Crear o actualizar lote si se proporciona
        lote_id = None
        if datos.get('numero_lote'):
            lote = LoteProducto.query.filter_by(
                producto_id=datos['producto_id'],
                numero_lote=datos['numero_lote']
            ).first()
            
            if lote:
                lote.cantidad_actual += datos['cantidad']
                lote.cantidad_inicial += datos['cantidad'] # Sumamos al inicial para tracking
                if datos.get('fecha_vencimiento'):
                    lote.fecha_vencimiento = datos['fecha_vencimiento']
            else:
                lote = LoteProducto(
                    producto_id=datos['producto_id'],
                    numero_lote=datos['numero_lote'],
                    fecha_vencimiento=datos.get('fecha_vencimiento'),
                    cantidad_inicial=datos['cantidad'],
                    cantidad_actual=datos['cantidad'],
                    costo_lote=datos['costo_unitario'],
                    proveedor_id=datos.get('proveedor_id'),
                    notas=datos.get('notas')
                )
                db.session.add(lote)
            
            db.session.flush() # Para obtener el ID del lote
            lote_id = lote.id

        # Crear movimiento
        movimiento = MovimientoInventario(
            producto_id=datos['producto_id'],
            usuario_id=usuario_id,
            proveedor_id=datos.get('proveedor_id'),
            lote_id=lote_id,
            tipo_movimiento='COMPRA',
            cantidad=datos['cantidad'],
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=producto.cantidad_actual,
            costo_unitario=datos['costo_unitario'],
            costo_total=datos['cantidad'] * datos['costo_unitario'],
            referencia_id=datos.get('referencia_id'),
            notas=datos.get('notas'),
                fecha_movimiento=datetime.now()
        )
        
        db.session.add(movimiento)
        
        # Resetear flag de notificación si el stock ahora es suficiente
        if producto.cantidad_actual > producto.stock_minimo:
            producto.alerta_stock_bajo_notificada = False
            
        db.session.commit()
        
        # Verificar márgenes y alertar de forma proactiva
        ServicioAlertas.verificar_y_alertar_margen(producto.id)
        if lote_id:
            ServicioAlertas.verificar_y_alertar_vencimiento(lote_id)
        
        # Registrar en auditoría
        registrar_accion_auditoria(
            accion='CREAR',
            tabla_afectada='movimientos_inventario',
            registro_id=movimiento.id,
            valores_nuevos=movimiento.to_dict()
        )
        
        return {
            'mensaje': 'Ingreso registrado exitosamente',
            'movimiento': movimiento.to_dict(),
            'costo_promedio': resultado_costo,
            'analisis_precio': analisis_precio,
            'producto_actualizado': producto.to_dict()
        }, 201


@inventario_ns.route('/salida')
class SalidaInventario(Resource):
    @jwt_required()
    @inventario_ns.expect(modelo_salida)
    @validate_request(SalidaSchema)
    def post(self):
        """Registra salida de mercancía (venta)."""
        datos = request.get_json()
        usuario_id = int(get_jwt_identity())
        
        producto = Producto.query.get(datos['producto_id'])
        if not producto:
            inventario_ns.abort(404, 'Producto no encontrado')
        
        # Validar stock disponible
        if producto.cantidad_actual < datos['cantidad']:
            inventario_ns.abort(400, f'Stock insuficiente. Disponible: {producto.cantidad_actual}')
        
        # Calcular ganancia real
        ganancia_info = CalculadoraCosto.calcular_ganancia_real_venta(
            datos['producto_id'],
            datos['cantidad'],
            datos['precio_unitario']
        )
        
        # Actualizar stock
        cantidad_anterior = producto.cantidad_actual
        producto.cantidad_actual -= datos['cantidad']
        
        # Crear movimiento
        movimiento = MovimientoInventario(
            producto_id=datos['producto_id'],
            usuario_id=usuario_id,
            tipo_movimiento='VENTA',
            cantidad=-datos['cantidad'],  # Negativo para salida
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=producto.cantidad_actual,
            costo_unitario=ganancia_info['costo_unitario'],
            costo_total=ganancia_info['costo_total'],
            precio_unitario=datos['precio_unitario'],
            precio_total=ganancia_info['ingreso_total'],
            referencia_id=datos.get('referencia_id'),
            notas=datos.get('notas'),
                fecha_movimiento=datetime.now()
        )
        
        db.session.add(movimiento)
        db.session.commit()
        
        # Registrar en auditoría
        registrar_accion_auditoria(
            accion='CREAR',
            tabla_afectada='movimientos_inventario',
            registro_id=movimiento.id,
            valores_nuevos=movimiento.to_dict()
        )
        
        return {
            'mensaje': 'Venta registrada exitosamente',
            'movimiento': movimiento.to_dict(),
            'ganancia': ganancia_info,
            'producto_actualizado': producto.to_dict()
        }, 201


@inventario_ns.route('/venta-multiple')
class VentaMultiple(Resource):
    @jwt_required()
    @inventario_ns.expect(modelo_venta_multiple)
    @validate_request(VentaMultipleSchema)
    def post(self):
        """Registra una venta de múltiples productos en una sola transacción."""
        datos = request.get_json()
        usuario_id = int(get_jwt_identity())
        items = datos.get('items', [])
        referencia_id = datos.get('referencia_id', f"VENTA-{datetime.now().strftime('%Y%m%d%H%M')}")
        notas_globales = datos.get('notas', '')
        
        if not items:
            inventario_ns.abort(400, 'La lista de items no puede estar vacía')
            
        resultados = []
        fecha = datetime.utcnow()
        
        try:
            for item in items:
                producto = Producto.query.get(item['producto_id'])
                if not producto:
                    continue
                
                # Validar stock
                if producto.cantidad_actual < item['cantidad']:
                    db.session.rollback()
                    inventario_ns.abort(400, f"Stock insuficiente para {producto.nombre}. Disponible: {producto.cantidad_actual}")
                
                # Calcular ganancia
                ganancia_info = CalculadoraCosto.calcular_ganancia_real_venta(
                    item['producto_id'],
                    item['cantidad'],
                    item['precio_unitario']
                )
                
                # Actualizar stock
                cantidad_anterior = producto.cantidad_actual
                producto.cantidad_actual -= item['cantidad']
                
                # Crear movimiento
                movimiento = MovimientoInventario(
                    producto_id=item['producto_id'],
                    usuario_id=usuario_id,
                    tipo_movimiento='VENTA',
                    cantidad=-item['cantidad'],
                    cantidad_anterior=cantidad_anterior,
                    cantidad_nueva=producto.cantidad_actual,
                    costo_unitario=ganancia_info['costo_unitario'],
                    costo_total=ganancia_info['costo_total'],
                    precio_unitario=item['precio_unitario'],
                    precio_total=ganancia_info['ingreso_total'],
                    referencia_id=referencia_id,
                    notas=f"{notas_globales} (Venta en lote)".strip(),
                    fecha_movimiento=fecha
                )
                
                db.session.add(movimiento)
                resultados.append({
                    'producto': producto.nombre,
                    'cantidad': item['cantidad'],
                    'total': ganancia_info['ingreso_total']
                })
            
            db.session.commit()
            
            # Registrar acción general en auditoría
            registrar_accion_auditoria(
                accion='CREAR',
                tabla_afectada='movimientos_inventario',
                registro_id=0, # ID 0 para transacciones múltiples
                valores_nuevos={'transaccion': 'Venta Múltiple', 'items': resultados, 'referencia': referencia_id}
            )
            
            return {
                'mensaje': 'Venta múltiple registrada exitosamente',
                'referencia': referencia_id,
                'items_procesados': len(resultados),
                'total_transaccion': sum(r['total'] for r in resultados)
            }, 201
            
        except Exception as e:
            db.session.rollback()
            inventario_ns.abort(500, f"Error al procesar venta múltiple: {str(e)}")


@inventario_ns.route('/ajuste')
class AjusteInventario(Resource):
    @jwt_required()
    @inventario_ns.expect(modelo_ajuste)
    @validate_request(AjusteSchema)
    def post(self):
        """Registra ajuste de inventario (merma, daño, etc)."""
        datos = request.get_json()
        usuario_id = int(get_jwt_identity())
        
        producto = Producto.query.get(datos['producto_id'])
        if not producto:
            inventario_ns.abort(404, 'Producto no encontrado')
        
        cantidad_anterior = producto.cantidad_actual
        producto.cantidad_actual += datos['cantidad']  # Puede ser positivo o negativo
        
        # Validar que no quede negativo
        if producto.cantidad_actual < 0:
            inventario_ns.abort(400, 'El ajuste resultaría en stock negativo')
        
        # Crear movimiento
        movimiento = MovimientoInventario(
            producto_id=datos['producto_id'],
            usuario_id=usuario_id,
            tipo_movimiento='AJUSTE',
            cantidad=datos['cantidad'],
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=producto.cantidad_actual,
            motivo_ajuste=datos['motivo_ajuste'],
            costo_unitario=producto.costo_promedio,
            costo_total=abs(datos['cantidad']) * float(producto.costo_promedio),
            notas=datos.get('notas'),
                fecha_movimiento=datetime.now()
        )
        
        db.session.add(movimiento)
        
        # Resetear flag de notificación si el stock aumenta por encima del mínimo
        if datos['cantidad'] > 0 and producto.cantidad_actual > producto.stock_minimo:
            producto.alerta_stock_bajo_notificada = False
            
        db.session.commit()
        
        # Registrar en auditoría
        registrar_accion_auditoria(
            accion='CREAR',
            tabla_afectada='movimientos_inventario',
            registro_id=movimiento.id,
            valores_nuevos=movimiento.to_dict()
        )
        
        return {
            'mensaje': 'Ajuste registrado exitosamente',
            'movimiento': movimiento.to_dict(),
            'producto_actualizado': producto.to_dict()
        }, 201


@inventario_ns.route('/auditoria-ciega')
class AuditoriaCiega(Resource):
    @jwt_required()
    def post(self):
        """Inicia una auditoría ciega seleccionando productos aleatorios."""
        cantidad = request.args.get('cantidad', 2, type=int)
        productos = ServicioAuditoriaCiega.seleccionar_productos_auditoria(cantidad)
        
        return {
            'mensaje': f'Se seleccionaron {len(productos)} productos para auditoría',
            'productos': productos
        }


@inventario_ns.route('/registrar-conteo')
class RegistrarConteo(Resource):
    @jwt_required()
    def post(self):
        """Registra el conteo físico de una auditoría."""
        datos = request.get_json()
        usuario_id = int(get_jwt_identity())
        
        resultado = ServicioAuditoriaCiega.registrar_conteo_auditoria(
            datos['producto_id'],
            datos['cantidad_fisica'],
            usuario_id,
            datos.get('notas')
        )
        
        return resultado


@inventario_ns.route('/balance')
class BalanceInventario(Resource):
    @jwt_required()
    def get(self):
        """Obtiene balance actual del inventario."""
        productos = Producto.query.filter_by(esta_activo=True).all()
        
        valor_total = sum(p.valor_inventario for p in productos)
        productos_bajo_stock = sum(1 for p in productos if p.esta_bajo_stock)
        
        return {
            'total_productos': len(productos),
            'valor_total_inventario': round(valor_total, 2),
            'productos_bajo_stock': productos_bajo_stock,
            'porcentaje_bajo_stock': round((productos_bajo_stock / len(productos) * 100) if productos else 0, 2)
        }


@inventario_ns.route('/reporte-dinero-dormido')
class ReporteDineroDormido(Resource):
    @jwt_required()
    def get(self):
        """Obtiene reporte de dinero dormido (productos sin movimiento)."""
        dias = request.args.get('dias', 60, type=int)
        resultado = ServicioDineroDormido.calcular_total_dinero_dormido(dias)
        
        return resultado
@inventario_ns.route('/tasa-cambio')
class GestionTasaCambio(Resource):
    @jwt_required()
    def get(self):
        """Obtiene la tasa de cambio actual y la actualiza si es necesario."""
        # Se puede forzar actualización con un parámetro ?actualizar=true
        forzar = request.args.get('actualizar', 'false').lower() == 'true'
        
        if forzar:
            TasaCambioServicio.obtener_tasa_bcv(forzar=True)
        else:
            # Intentar obtener (el servicio manejará la caché de 1 hora)
            TasaCambioServicio.obtener_tasa_bcv(forzar=False)
        
        return TasaCambioServicio.get_info_tasa()

    @jwt_required()
    @inventario_ns.expect(modelo_tasa)
    def post(self):
        """Actualiza manualmente la tasa de cambio."""
        datos = request.get_json()
        TasaCambioServicio.actualizar_tasa(datos['tasa'])
        
        # Auditoría
        registrar_accion_auditoria(
            accion='ACTUALIZAR',
            tabla_afectada='configuraciones',
            registro_id=0,
            valores_nuevos={'clave': 'tasa_dolar_bcv', 'valor': datos['tasa']}
        )
        
        return {
            'mensaje': 'Tasa de cambio actualizada manualmente',
            'nueva_tasa': TasaCambioServicio.get_info_tasa()
        }
@inventario_ns.route('/desempacar')
class DesempacarInventario(Resource):
    @jwt_required()
    def post(self):
        """
        Operación de fraccionamiento: Desempaca 1 unidad de un producto 'Padre' (caja)
        y la convierte en N unidades del producto 'Hijo' (unidad individual).
        """
        datos = request.get_json()
        usuario_id = int(get_jwt_identity())
        producto_hijo_id = datos.get('producto_id')
        cantidad_a_desempacar = datos.get('cantidad', 1) # Por defecto 1 caja
        
        producto_hijo = Producto.query.get(producto_hijo_id)
        if not producto_hijo:
            inventario_ns.abort(404, 'Producto no encontrado')
            
        if not producto_hijo.padre:
            inventario_ns.abort(400, 'Este producto no tiene un producto padre configurado para fraccionamiento')
            
        producto_padre = producto_hijo.padre
        factor = producto_hijo.factor_conversion or 1.0
        
        # Validar stock del padre
        if producto_padre.cantidad_actual < cantidad_a_desempacar:
            inventario_ns.abort(400, f'Stock insuficiente de {producto_padre.nombre}. Disponible: {producto_padre.cantidad_actual} {producto_padre.unidad_medida}')
            
        try:
            # 1. Restar del padre (Salida por fraccionamiento)
            cant_anterior_padre = producto_padre.cantidad_actual
            producto_padre.cantidad_actual -= cantidad_a_desempacar
            
            mov_padre = MovimientoInventario(
                producto_id=producto_padre.id,
                usuario_id=usuario_id,
                tipo_movimiento='AJUSTE',
                motivo_ajuste='FRACCIONAMIENTO_SALIDA',
                cantidad=-cantidad_a_desempacar,
                cantidad_anterior=cant_anterior_padre,
                cantidad_nueva=producto_padre.cantidad_actual,
                costo_unitario=producto_padre.costo_promedio,
                costo_total=cantidad_a_desempacar * float(producto_padre.costo_promedio),
                notas=f"Fraccionamiento: Convertido a {producto_hijo.nombre}",
                    fecha_movimiento=datetime.now()
            )
            db.session.add(mov_padre)
            
            # 2. Sumar al hijo (Entrada por fraccionamiento)
            cantidad_hijo_nueva = cantidad_a_desempacar * factor
            cant_anterior_hijo = producto_hijo.cantidad_actual
            producto_hijo.cantidad_actual += cantidad_hijo_nueva
            
            # El costo unitario del hijo se hereda del padre pro-rateado
            costo_unitario_hijo = float(producto_padre.costo_promedio) / factor if factor > 0 else 0
            producto_hijo.costo_promedio = costo_unitario_hijo
            
            mov_hijo = MovimientoInventario(
                producto_id=producto_hijo.id,
                usuario_id=usuario_id,
                tipo_movimiento='AJUSTE',
                motivo_ajuste='FRACCIONAMIENTO_ENTRADA',
                cantidad=cantidad_hijo_nueva,
                cantidad_anterior=cant_anterior_hijo,
                cantidad_nueva=producto_hijo.cantidad_actual,
                costo_unitario=costo_unitario_hijo,
                costo_total=cantidad_hijo_nueva * costo_unitario_hijo,
                notas=f"Fraccionamiento: Desempacado de {producto_padre.nombre}",
                fecha_movimiento=datetime.utcnow()
            )
            db.session.add(mov_hijo)
            
            db.session.commit()
            
            # Auditoría
            registrar_accion_auditoria(
                accion='ACTUALIZAR',
                tabla_afectada='productos',
                registro_id=producto_hijo.id,
                valores_nuevos={'operacion': 'fraccionamiento', 'padre_id': producto_padre.id, 'cantidad_desempacada': cantidad_a_desempacar}
            )
            
            return {
                'mensaje': 'Fraccionamiento completado exitosamente',
                'producto_hijo': producto_hijo.to_dict(),
                'producto_padre': producto_padre.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            inventario_ns.abort(500, f"Error al procesar fraccionamiento: {str(e)}")
