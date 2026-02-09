"""
Servicio de Predicción de Agotamiento.
Analiza ventas históricas y predice cuándo se agotará un producto.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func
from app.core.extensions import db
from app.models import Producto, MovimientoInventario


class ServicioPrediccion:
    """Servicio de forecasting y predicción de agotamiento."""
    
    @staticmethod
    def predecir_agotamiento(producto_id, dias_analisis=30):
        """
        Predice cuándo se agotará un producto basado en ventas históricas.
        
        Args:
            producto_id: ID del producto
            dias_analisis: Días hacia atrás para analizar (default 30)
            
        Returns:
            dict con predicción y recomendaciones
        """
        producto = Producto.query.get(producto_id)
        if not producto:
            raise ValueError(f'Producto con ID {producto_id} no encontrado')
        
        # Obtener fecha límite para análisis
        fecha_limite = datetime.utcnow() - timedelta(days=dias_analisis)
        
        # Obtener ventas en el período
        ventas = MovimientoInventario.query.filter(
            MovimientoInventario.producto_id == producto_id,
            MovimientoInventario.tipo_movimiento == 'VENTA',
            MovimientoInventario.fecha_movimiento >= fecha_limite,
            MovimientoInventario.esta_activo == True
        ).all()
        
        if not ventas:
            return {
                'tiene_datos': False,
                'mensaje': 'No hay suficientes datos de ventas para hacer predicción',
                'dias_hasta_agotar': None,
                'velocidad_venta_diaria': 0,
                'fecha_agotamiento_estimada': None,
                'requiere_pedido': False
            }
        
        # Calcular total vendido
        total_vendido = sum(abs(venta.cantidad) for venta in ventas)
        
        # Calcular velocidad de venta diaria
        velocidad_venta_diaria = total_vendido / dias_analisis
        
        # Predecir días hasta agotamiento
        if velocidad_venta_diaria > 0:
            dias_hasta_agotar = producto.cantidad_actual / velocidad_venta_diaria
            fecha_agotamiento = datetime.utcnow() + timedelta(days=dias_hasta_agotar)
        else:
            dias_hasta_agotar = None
            fecha_agotamiento = None
        
        # Determinar si requiere pedido (menos de 7 días)
        requiere_pedido = dias_hasta_agotar is not None and dias_hasta_agotar < 7
        
        # Calcular cantidad sugerida para pedido (para 30 días)
        cantidad_sugerida = velocidad_venta_diaria * 30
        
        return {
            'tiene_datos': True,
            'producto_id': producto_id,
            'producto_nombre': producto.nombre,
            'stock_actual': producto.cantidad_actual,
            'total_vendido_periodo': total_vendido,
            'dias_analisis': dias_analisis,
            'velocidad_venta_diaria': round(velocidad_venta_diaria, 2),
            'dias_hasta_agotar': round(dias_hasta_agotar, 1) if dias_hasta_agotar else None,
            'fecha_agotamiento_estimada': fecha_agotamiento.isoformat() if fecha_agotamiento else None,
            'requiere_pedido': requiere_pedido,
            'cantidad_sugerida_pedido': round(cantidad_sugerida, 2),
            'nivel_urgencia': ServicioPrediccion._calcular_urgencia(dias_hasta_agotar)
        }
    
    @staticmethod
    def _calcular_urgencia(dias_hasta_agotar):
        """Calcula el nivel de urgencia basado en días hasta agotamiento."""
        if dias_hasta_agotar is None:
            return 'SIN_DATOS'
        elif dias_hasta_agotar <= 0:
            return 'AGOTADO'
        elif dias_hasta_agotar < 3:
            return 'CRITICO'
        elif dias_hasta_agotar < 7:
            return 'URGENTE'
        elif dias_hasta_agotar < 14:
            return 'ATENCION'
        else:
            return 'NORMAL'
    
    @staticmethod
    def obtener_productos_criticos(limite=10):
        """
        Obtiene los productos más críticos que requieren atención.
        Optimizado para evitar problemas de N+1.
        """
        # 1. Obtener todos los productos activos (incluyendo stock <= 0)
        productos = Producto.query.filter(
            Producto.esta_activo == True
        ).all()
        
        if not productos:
            return []

        # 2. Obtener TODAS las ventas de los últimos 30 días en UNA sola consulta
        fecha_limite = datetime.utcnow() - timedelta(days=30)
        ventas_totales = db.session.query(
            MovimientoInventario.producto_id,
            func.sum(func.abs(MovimientoInventario.cantidad)).label('total_vendido')
        ).filter(
            MovimientoInventario.tipo_movimiento == 'VENTA',
            MovimientoInventario.fecha_movimiento >= fecha_limite,
            MovimientoInventario.esta_activo == True
        ).group_by(MovimientoInventario.producto_id).all()
        
        # Mapear ventas por producto_id para acceso rápido
        ventas_map = {v.producto_id: float(v.total_vendido) for v in ventas_totales}
        
        predicciones = []
        for producto in productos:
            try:
                # Caso especial: Stock cero o negativo es siempre crítico
                if producto.cantidad_actual <= 0:
                    predicciones.append({
                        'tiene_datos': True,
                        'producto_id': producto.id,
                        'producto_nombre': producto.nombre,
                        'stock_actual': producto.cantidad_actual,
                        'stock_minimo': producto.stock_minimo,
                        'total_vendido_periodo': ventas_map.get(producto.id, 0),
                        'dias_analisis': 30,
                        'velocidad_venta_diaria': round(ventas_map.get(producto.id, 0) / 30, 2),
                        'dias_hasta_agotar': 0,
                        'fecha_agotamiento_estimada': datetime.utcnow().isoformat(),
                        'requiere_pedido': True,
                        'cantidad_sugerida_pedido': round((ventas_map.get(producto.id, 0) / 30) * 30, 2) or 10,
                        'nivel_urgencia': 'AGOTADO'
                    })
                    continue

                # Usar datos pre-calculados para el resto
                total_vendido = ventas_map.get(producto.id, 0)
                
                # Si no tiene ventas pero está bajo el stock mínimo, también es importante
                if total_vendido == 0:
                    if producto.esta_bajo_stock:
                        predicciones.append({
                            'tiene_datos': False,
                            'producto_id': producto.id,
                            'producto_nombre': producto.nombre,
                            'stock_actual': producto.cantidad_actual,
                            'stock_minimo': producto.stock_minimo,
                            'total_vendido_periodo': 0,
                            'dias_analisis': 30,
                            'velocidad_venta_diaria': 0,
                            'dias_hasta_agotar': None,
                            'fecha_agotamiento_estimada': None,
                            'requiere_pedido': True,
                            'cantidad_sugerida_pedido': producto.stock_minimo * 2,
                            'nivel_urgencia': 'URGENTE'
                        })
                    continue
                
                velocidad_venta_diaria = total_vendido / 30
                dias_hasta_agotar = producto.cantidad_actual / velocidad_venta_diaria
                
                # Si se agota en menos de 7 días o ya está bajo el mínimo
                if dias_hasta_agotar < 7 or producto.esta_bajo_stock:
                    fecha_agotamiento = datetime.utcnow() + timedelta(days=dias_hasta_agotar)
                    predicciones.append({
                        'tiene_datos': True,
                        'producto_id': producto.id,
                        'producto_nombre': producto.nombre,
                        'stock_actual': producto.cantidad_actual,
                        'stock_minimo': producto.stock_minimo,
                        'total_vendido_periodo': total_vendido,
                        'dias_analisis': 30,
                        'velocidad_venta_diaria': round(velocidad_venta_diaria, 2),
                        'dias_hasta_agotar': round(dias_hasta_agotar, 1),
                        'fecha_agotamiento_estimada': fecha_agotamiento.isoformat(),
                        'requiere_pedido': True,
                        'cantidad_sugerida_pedido': round(velocidad_venta_diaria * 30, 2),
                        'nivel_urgencia': ServicioPrediccion._calcular_urgencia(dias_hasta_agotar)
                    })
            except Exception:
                continue
        
        # Ordenar por urgencia
        orden_urgencia = {'AGOTADO': 0, 'CRITICO': 1, 'URGENTE': 2, 'ATENCION': 3, 'NORMAL': 4, 'SIN_DATOS': 5}
        predicciones.sort(key=lambda x: (orden_urgencia.get(x['nivel_urgencia'], 99), x['dias_hasta_agotar'] or 999))
        
        return predicciones[:limite]
