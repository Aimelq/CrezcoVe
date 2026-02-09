"""
Servicio de Dinero Dormido.
Identifica productos sin movimiento que inmovilizan capital.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func
from app.core.extensions import db
from app.models import Producto, MovimientoInventario


class ServicioDineroDormido:
    """Servicio para identificar dinero inmovilizado en inventario."""
    
    @staticmethod
    def identificar_productos_sin_movimiento(dias_sin_movimiento=60, limite=20):
        """
        Identifica productos sin ventas en X días.
        
        Args:
            dias_sin_movimiento: Días sin movimiento para considerar (default 60)
            limite: Número máximo de productos a retornar
            
        Returns:
            Lista de productos con dinero dormido
        """
        fecha_limite = datetime.utcnow() - timedelta(days=dias_sin_movimiento)
        
        # Obtener productos activos con stock
        productos = Producto.query.filter(
            Producto.esta_activo == True,
            Producto.cantidad_actual > 0
        ).all()
        
        productos_dormidos = []
        
        for producto in productos:
            # IGNORAR productos nuevos (creados en los últimos N días)
            # Esto evita dar sugerencias falsas sobre productos recién registrados
            if producto.creado_en >= fecha_limite:
                continue

            # Verificar si tiene ventas recientes
            ultima_venta = MovimientoInventario.query.filter(
                MovimientoInventario.producto_id == producto.id,
                MovimientoInventario.tipo_movimiento == 'VENTA',
                MovimientoInventario.fecha_movimiento >= fecha_limite
            ).first()
            
            # Si no tiene ventas recientes, es dinero dormido
            if not ultima_venta:
                # Calcular valor inmovilizado
                valor_inmovilizado = float(producto.costo_promedio) * producto.cantidad_actual
                
                # Obtener fecha de última venta (si existe)
                ultima_venta_historica = MovimientoInventario.query.filter(
                    MovimientoInventario.producto_id == producto.id,
                    MovimientoInventario.tipo_movimiento == 'VENTA'
                ).order_by(MovimientoInventario.fecha_movimiento.desc()).first()
                
                dias_sin_venta = None
                if ultima_venta_historica:
                    delta = datetime.utcnow() - ultima_venta_historica.fecha_movimiento
                    dias_sin_venta = delta.days
                
                # Calcular descuento sugerido para liquidar
                descuento_sugerido = ServicioDineroDormido._calcular_descuento_sugerido(dias_sin_venta)
                precio_con_descuento = float(producto.precio_venta) * (1 - descuento_sugerido / 100)
                
                productos_dormidos.append({
                    'producto_id': producto.id,
                    'codigo_sku': producto.codigo_sku,
                    'nombre': producto.nombre,
                    'cantidad_actual': producto.cantidad_actual,
                    'costo_promedio': float(producto.costo_promedio),
                    'precio_venta': float(producto.precio_venta),
                    'valor_inmovilizado': round(valor_inmovilizado, 2),
                    'dias_sin_venta': dias_sin_venta,
                    'ultima_venta': ultima_venta_historica.fecha_movimiento.isoformat() if ultima_venta_historica else None,
                    'descuento_sugerido_porcentaje': descuento_sugerido,
                    'precio_con_descuento': round(precio_con_descuento, 2),
                    'recomendacion': ServicioDineroDormido._generar_recomendacion(
                        producto.nombre, dias_sin_venta, valor_inmovilizado, descuento_sugerido
                    )
                })
        
        # Ordenar por valor inmovilizado (mayor a menor)
        productos_dormidos.sort(key=lambda x: x['valor_inmovilizado'], reverse=True)
        
        return productos_dormidos[:limite]
    
    @staticmethod
    def _calcular_descuento_sugerido(dias_sin_venta):
        """
        Calcula el descuento sugerido basado en días sin venta.
        
        Args:
            dias_sin_venta: Días sin venta
            
        Returns:
            Porcentaje de descuento sugerido
        """
        if dias_sin_venta is None:
            return 10
        elif dias_sin_venta > 180:
            return 30  # 30% de descuento para productos muy viejos
        elif dias_sin_venta > 120:
            return 20  # 20% para productos viejos
        elif dias_sin_venta > 60:
            return 15  # 15% para productos sin movimiento moderado
        else:
            return 10  # 10% mínimo
    
    @staticmethod
    def _generar_recomendacion(nombre, dias_sin_venta, valor_inmovilizado, descuento):
        """Genera recomendación personalizada."""
        if dias_sin_venta and dias_sin_venta > 180:
            urgencia = "🔴 URGENTE"
        elif dias_sin_venta and dias_sin_venta > 120:
            urgencia = "🟠 ALTA PRIORIDAD"
        else:
            urgencia = "🟡 CONSIDERAR"
        
        return f"{urgencia}: El producto '{nombre}' tiene ${valor_inmovilizado:.2f} en inventario sin movimiento. " \
               f"Considera una oferta del {descuento}% para liberar capital y espacio."
    
    @staticmethod
    def calcular_total_dinero_dormido(dias_sin_movimiento=60):
        """
        Calcula el total de dinero inmovilizado en inventario.
        
        Args:
            dias_sin_movimiento: Días sin movimiento
            
        Returns:
            dict con totales
        """
        productos_dormidos = ServicioDineroDormido.identificar_productos_sin_movimiento(
            dias_sin_movimiento, limite=9999
        )
        
        total_valor = sum(p['valor_inmovilizado'] for p in productos_dormidos)
        total_productos = len(productos_dormidos)
        
        return {
            'total_productos_sin_movimiento': total_productos,
            'valor_total_inmovilizado': round(total_valor, 2),
            'dias_analisis': dias_sin_movimiento,
            'productos': productos_dormidos[:10]  # Top 10
        }
