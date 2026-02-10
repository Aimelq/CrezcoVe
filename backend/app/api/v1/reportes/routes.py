"""
Endpoints de Reportes.
Genera reportes y estadísticas del sistema.
"""
from datetime import datetime, timedelta
from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from app.core.extensions import db
from app.models import Producto, MovimientoInventario, Alerta
from app.services.prediccion_agotamiento import ServicioPrediccion

# Crear namespace
reportes_ns = Namespace('reportes', description='Reportes y estadísticas')


@reportes_ns.route('/dashboard')
class Dashboard(Resource):
    @jwt_required()
    def get(self):
        """Obtiene datos para el dashboard principal."""
        # Valor total del inventario
        productos = Producto.query.filter_by(esta_activo=True).all()
        valor_total = sum(p.valor_inventario for p in productos)
        
        # Productos por agotarse
        productos_criticos = ServicioPrediccion.obtener_productos_criticos(limite=10)
        
        # Pérdidas del mes (anteriormente mermas)
        fecha_inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        perdidas_mes = db.session.query(func.sum(MovimientoInventario.costo_total)).filter(
            MovimientoInventario.tipo_movimiento.in_(['MERMA', 'AJUSTE']),
            MovimientoInventario.cantidad < 0,
            MovimientoInventario.fecha_movimiento >= fecha_inicio_mes
        ).scalar() or 0
        
        # Ganancia del día
        hoy_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ventas_hoy = MovimientoInventario.query.filter(
            MovimientoInventario.tipo_movimiento == 'VENTA',
            MovimientoInventario.fecha_movimiento >= hoy_inicio
        ).all()
        ganancia_hoy = sum(v.ganancia for v in ventas_hoy)
        
        # Alertas activas
        alertas_activas = Alerta.query.filter_by(esta_resuelta=False, esta_activo=True).count()
        
        return {
            'valor_total_inventario': round(valor_total, 2),
            'total_productos': len(productos),
            'productos_criticos': len(productos_criticos),
            'perdidas_mes': round(float(perdidas_mes), 2),
            'ganancia_hoy': round(ganancia_hoy, 2),
            'alertas_activas': alertas_activas
        }


@reportes_ns.route('/movimientos-7-dias')
class Movimientos7Dias(Resource):
    @jwt_required()
    def get(self):
        """Obtiene movimientos de los últimos 7 días para gráfico."""
        fecha_limite = datetime.now() - timedelta(days=7)
        
        movimientos = MovimientoInventario.query.filter(
            MovimientoInventario.fecha_movimiento >= fecha_limite
        ).all()
        
        # Agrupar por día y tipo
        datos_por_dia = {}
        for mov in movimientos:
            fecha_str = mov.fecha_movimiento.strftime('%Y-%m-%d')
            if fecha_str not in datos_por_dia:
                datos_por_dia[fecha_str] = {
                    'fecha': fecha_str,
                    'entradas': 0,
                    'salidas': 0,
                    'valor_entradas': 0,
                    'valor_salidas': 0
                }
            
            if mov.es_entrada:
                datos_por_dia[fecha_str]['entradas'] += abs(mov.cantidad)
                if mov.costo_total:
                    datos_por_dia[fecha_str]['valor_entradas'] += float(mov.costo_total)
            elif mov.es_salida:
                datos_por_dia[fecha_str]['salidas'] += abs(mov.cantidad)
                if mov.precio_total:
                    datos_por_dia[fecha_str]['valor_salidas'] += float(mov.precio_total)
        
        # Convertir a lista ordenada
        datos_lista = sorted(datos_por_dia.values(), key=lambda x: x['fecha'])
        
        return {
            'movimientos': datos_lista
        }


@reportes_ns.route('/productos-criticos')
class ProductosCriticos(Resource):
    @jwt_required()
    def get(self):
        """Obtiene productos críticos que requieren atención."""
        limite = request.args.get('limite', 20, type=int)
        productos_criticos = ServicioPrediccion.obtener_productos_criticos(limite)
        
        return {
            'productos_criticos': productos_criticos,
            'total': len(productos_criticos)
        }


@reportes_ns.route('/alertas-activas')
class AlertasActivas(Resource):
    @jwt_required()
    def get(self):
        """Obtiene alertas activas del sistema."""
        alertas = Alerta.query.filter_by(
            esta_resuelta=False,
            esta_activo=True
        ).order_by(Alerta.creado_en.desc()).limit(50).all()
        
        return {
            'alertas': [a.to_dict() for a in alertas],
            'total': len(alertas)
        }
