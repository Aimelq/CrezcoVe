"""
Servicio de Asistente de Precios.
Detecta inflación y sugiere ajustes de precio para mantener margen.
"""
from decimal import Decimal, ROUND_HALF_UP
from app.models import Producto


class AsistentePrecios:
    """Servicio para asistencia en ajuste de precios."""
    
    @staticmethod
    def analizar_impacto_costo(producto_id, nuevo_costo):
        """
        Analiza el impacto de un nuevo costo en el margen de ganancia.
        
        Args:
            producto_id: ID del producto
            nuevo_costo: Nuevo costo de compra
            
        Returns:
            dict con análisis y sugerencias
        """
        producto = Producto.query.get(producto_id)
        if not producto:
            raise ValueError(f'Producto con ID {producto_id} no encontrado')
        
        costo_actual = Decimal(str(producto.costo_promedio))
        ultimo_costo = Decimal(str(producto.ultimo_costo_compra)) if producto.ultimo_costo_compra else Decimal('0')
        
        # Usar el mayor entre costo promedio y último costo como referencia base
        costo_referencia = max(costo_actual, ultimo_costo)
        
        precio_venta_actual = Decimal(str(producto.precio_venta))
        margen_deseado = Decimal(str(producto.margen_deseado))
        nuevo_costo_dec = Decimal(str(nuevo_costo))
        
        # Calcular margen actual
        if costo_actual > 0:
            margen_actual = ((precio_venta_actual - costo_actual) / costo_actual) * 100
        else:
            margen_actual = Decimal('0')
        
        # Calcular margen con nuevo costo (manteniendo precio actual)
        if nuevo_costo_dec > 0:
            margen_con_nuevo_costo = ((precio_venta_actual - nuevo_costo_dec) / nuevo_costo_dec) * 100
        else:
            margen_con_nuevo_costo = Decimal('0')
        
        # Calcular precio sugerido para mantener margen deseado
        precio_sugerido = nuevo_costo_dec * (1 + (margen_deseado / 100))
        precio_sugerido = precio_sugerido.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Calcular variación de costo
        # Calcular variación de costo respecto a la referencia (última compra o promedio)
        if costo_referencia > 0:
            variacion_costo = ((nuevo_costo_dec - costo_referencia) / costo_referencia) * 100
        else:
            variacion_costo = Decimal('0')
        
        # Determinar si hay inflación significativa (> 5%)
        hay_inflacion = variacion_costo > 5
        
        # Determinar si el margen cae por debajo del deseado
        margen_afectado = margen_con_nuevo_costo < margen_deseado
        
        # Generar recomendación
        if hay_inflacion and margen_afectado:
            recomendacion = f"⚠️ INFLACIÓN DETECTADA: El costo aumentó {float(variacion_costo):.1f}%. " \
                          f"Tu margen bajaría del {float(margen_actual):.1f}% al {float(margen_con_nuevo_costo):.1f}%. " \
                          f"Se recomienda ajustar el precio de venta a ${float(precio_sugerido):.2f} " \
                          f"para mantener el margen deseado del {float(margen_deseado):.1f}%."
            requiere_atencion = True
        elif margen_afectado:
            recomendacion = f"⚠️ MARGEN AFECTADO: Con el nuevo costo, tu margen sería {float(margen_con_nuevo_costo):.1f}% " \
                          f"(menor al deseado de {float(margen_deseado):.1f}%). " \
                          f"Considera ajustar el precio a ${float(precio_sugerido):.2f}."
            requiere_atencion = True
        else:
            recomendacion = f"✅ El margen se mantiene saludable ({float(margen_con_nuevo_costo):.1f}%). " \
                          f"No se requiere ajuste de precio por ahora."
            requiere_atencion = False
        
        return {
            'producto_id': producto_id,
            'producto_nombre': producto.nombre,
            'costo_actual': float(costo_actual),
            'nuevo_costo': float(nuevo_costo_dec),
            'variacion_costo_porcentaje': float(variacion_costo.quantize(Decimal('0.01'))),
            'precio_venta_actual': float(precio_venta_actual),
            'margen_actual_porcentaje': float(margen_actual.quantize(Decimal('0.01'))),
            'margen_con_nuevo_costo_porcentaje': float(margen_con_nuevo_costo.quantize(Decimal('0.01'))),
            'margen_deseado_porcentaje': float(margen_deseado),
            'precio_sugerido': float(precio_sugerido),
            'aumento_precio_sugerido': float((precio_sugerido - precio_venta_actual).quantize(Decimal('0.01'))),
            'hay_inflacion': hay_inflacion,
            'margen_afectado': margen_afectado,
            'requiere_atencion': requiere_atencion,
            'recomendacion': recomendacion
        }
    
    @staticmethod
    def calcular_precio_con_margen(costo, margen_porcentaje):
        """
        Calcula el precio de venta dado un costo y margen deseado.
        
        Args:
            costo: Costo del producto
            margen_porcentaje: Margen de ganancia deseado (%)
            
        Returns:
            Precio de venta calculado
        """
        costo_dec = Decimal(str(costo))
        margen_dec = Decimal(str(margen_porcentaje))
        
        precio = costo_dec * (1 + (margen_dec / 100))
        return float(precio.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
