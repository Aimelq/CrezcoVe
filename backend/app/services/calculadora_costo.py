"""
Servicio de Calculadora de Costo Promedio Ponderado.
Implementa el algoritmo de cálculo de costo promedio.
"""
from decimal import Decimal, ROUND_HALF_UP
from app.core.extensions import db
from app.models import Producto, MovimientoInventario


class CalculadoraCosto:
    """Servicio para calcular costo promedio ponderado."""
    
    @staticmethod
    def calcular_nuevo_costo_promedio(producto_id, cantidad_nueva, costo_nuevo):
        """
        Calcula el nuevo costo promedio ponderado al recibir mercancía.
        
        Fórmula: (stock_actual * costo_actual + cantidad_nueva * costo_nuevo) / (stock_actual + cantidad_nueva)
        
        Args:
            producto_id: ID del producto
            cantidad_nueva: Cantidad de productos que ingresan
            costo_nuevo: Costo unitario de la nueva compra
            
        Returns:
            dict con el nuevo costo promedio y otros datos calculados
        """
        producto = Producto.query.get(producto_id)
        if not producto:
            raise ValueError(f'Producto con ID {producto_id} no encontrado')
        
        stock_actual = Decimal(str(producto.cantidad_actual))
        costo_actual = Decimal(str(producto.costo_promedio))
        cantidad_nueva_dec = Decimal(str(cantidad_nueva))
        costo_nuevo_dec = Decimal(str(costo_nuevo))
        
        # Si no hay stock actual, el nuevo costo es el costo promedio
        if stock_actual == 0:
            nuevo_costo_promedio = costo_nuevo_dec
        else:
            # Calcular costo promedio ponderado
            valor_stock_actual = stock_actual * costo_actual
            valor_compra_nueva = cantidad_nueva_dec * costo_nuevo_dec
            stock_total = stock_actual + cantidad_nueva_dec
            
            nuevo_costo_promedio = (valor_stock_actual + valor_compra_nueva) / stock_total
        
        # Redondear a 2 decimales
        nuevo_costo_promedio = nuevo_costo_promedio.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Calcular variación de costo
        if costo_actual > 0:
            variacion_porcentaje = ((costo_nuevo_dec - costo_actual) / costo_actual) * 100
        else:
            variacion_porcentaje = Decimal('0')
        
        return {
            'costo_promedio_anterior': float(costo_actual),
            'nuevo_costo_promedio': float(nuevo_costo_promedio),
            'costo_compra': float(costo_nuevo_dec),
            'variacion_porcentaje': float(variacion_porcentaje.quantize(Decimal('0.01'))),
            'hubo_aumento': costo_nuevo_dec > costo_actual
        }
    
    @staticmethod
    def actualizar_costo_producto(producto_id, cantidad_nueva, costo_nuevo):
        """
        Actualiza el costo promedio del producto en la base de datos.
        
        Args:
            producto_id: ID del producto
            cantidad_nueva: Cantidad que ingresa
            costo_nuevo: Costo unitario de la compra
            
        Returns:
            Producto actualizado
        """
        resultado = CalculadoraCosto.calcular_nuevo_costo_promedio(
            producto_id, cantidad_nueva, costo_nuevo
        )
        
        producto = Producto.query.get(producto_id)
        
        # Si hay aumento de costo significativo (> 5%), generar alerta
        if resultado['hubo_aumento'] and resultado['variacion_porcentaje'] > 5:
            from app.models import Alerta
            alerta = Alerta(
                producto_id=producto_id,
                tipo_alerta='INFLACION_DETECTADA',
                titulo=f"Inflación Detectada: {producto.nombre}",
                mensaje=f"El costo de {producto.nombre} aumentó un {resultado['variacion_porcentaje']:.1f}%. " 
                        f"Nuevo costo promedio: ${resultado['nuevo_costo_promedio']:.2f}. "
                        f"Considera ajustar el precio de venta.",
                prioridad='ALTA',
                datos_adicionales=resultado
            )
            db.session.add(alerta)
            
            # También notificar por Telegram
            from app.services.notificaciones_telegram import servicio_telegram
            from app.services.asistente_precios import AsistentePrecios
            analisis = AsistentePrecios.analizar_impacto_costo(producto_id, costo_nuevo)
            servicio_telegram.notificar_inflacion_detectada(
                producto.nombre,
                resultado['costo_promedio_anterior'],
                float(costo_nuevo),
                analisis['precio_sugerido']
            )

        producto.costo_promedio = Decimal(str(resultado['nuevo_costo_promedio']))
        producto.ultimo_costo_compra = Decimal(str(costo_nuevo))
        producto.cantidad_actual += cantidad_nueva
        
        db.session.commit()
        
        return producto
    
    @staticmethod
    def calcular_ganancia_real_venta(producto_id, cantidad_vendida, precio_venta):
        """
        Calcula la ganancia real de una venta usando el costo promedio actual.
        
        Args:
            producto_id: ID del producto
            cantidad_vendida: Cantidad vendida
            precio_venta: Precio de venta unitario
            
        Returns:
            dict con información de ganancia
        """
        producto = Producto.query.get(producto_id)
        if not producto:
            raise ValueError(f'Producto con ID {producto_id} no encontrado')
        
        costo_promedio = Decimal(str(producto.costo_promedio))
        cantidad_dec = Decimal(str(cantidad_vendida))
        precio_dec = Decimal(str(precio_venta))
        
        costo_total = costo_promedio * cantidad_dec
        ingreso_total = precio_dec * cantidad_dec
        ganancia = ingreso_total - costo_total
        
        if costo_total > 0:
            margen_porcentaje = (ganancia / costo_total) * 100
        else:
            margen_porcentaje = Decimal('0')
        
        return {
            'costo_unitario': float(costo_promedio),
            'costo_total': float(costo_total.quantize(Decimal('0.01'))),
            'precio_unitario': float(precio_dec),
            'ingreso_total': float(ingreso_total.quantize(Decimal('0.01'))),
            'ganancia': float(ganancia.quantize(Decimal('0.01'))),
            'margen_porcentaje': float(margen_porcentaje.quantize(Decimal('0.01')))
        }
