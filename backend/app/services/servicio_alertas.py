"""
Servicio de Alertas del Sistema.
Centraliza la creación de alertas y el envío de notificaciones proactivas.
"""
from datetime import datetime
from app.core.extensions import db
from app.models import Alerta, Producto
from app.services.notificaciones_telegram import servicio_telegram

class ServicioAlertas:
    """Centraliza la lógica de auditoría inteligente y alertas."""
    
    @staticmethod
    def crear_alerta(tipo_alerta, titulo, mensaje, prioridad='MEDIA', producto_id=None, datos_adicionales=None):
        """
        Crea una nueva alerta si no existe una idéntica no resuelta.
        Si existe, actualiza el mensaje y eleva la prioridad si es necesario.
        """
        # Evitar duplicados no resueltos para el mismo producto y tipo
        existente = Alerta.query.filter_by(
            producto_id=producto_id,
            tipo_alerta=tipo_alerta,
            esta_resuelta=False
        ).first()

        if existente:
            # Actualizar mensaje y fecha si ya existe
            existente.mensaje = mensaje
            # Mantener la prioridad más alta
            prioridades = ['BAJA', 'MEDIA', 'ALTA', 'CRITICA']
            if prioridades.index(prioridad) > prioridades.index(existente.prioridad):
                existente.prioridad = prioridad
            
            existente.creado_en = datetime.utcnow()
            db.session.commit()
            return existente

        # Crear nueva alerta
        alerta = Alerta(
            tipo_alerta=tipo_alerta,
            titulo=titulo,
            mensaje=mensaje,
            prioridad=prioridad,
            producto_id=producto_id,
            datos_adicionales=datos_adicionales
        )
        
        db.session.add(alerta)
        db.session.commit()

        # Enviar notificación proactiva si es alta prioridad o crítica
        if prioridad in ['ALTA', 'CRITICA']:
            ServicioAlertas._despachar_notificacion_proactiva(alerta)
        
        return alerta

    @staticmethod
    def _despachar_notificacion_proactiva(alerta):
        """Envía notificaciones a canales externos (Telegram)."""
        # Telegram
        prefijo = "🚨" if alerta.prioridad == 'ALTA' else "🔴"
        mensaje_tg = f"{prefijo} *{alerta.titulo}*\n\n{alerta.mensaje}"
        
        # Si tiene producto, añadir SKU para referencia
        if alerta.producto_id:
            producto = Producto.query.get(alerta.producto_id)
            if producto:
                mensaje_tg += f"\n\n📦 *SKU:* `{producto.codigo_sku}`"
        
        servicio_telegram.enviar_mensaje(mensaje_tg)

    @staticmethod
    def verificar_y_alertar_margen(producto_id):
        """Verifica el margen de un producto y genera alerta si es crítico."""
        producto = Producto.query.get(producto_id)
        if not producto:
            return
            
        costo = float(producto.costo_promedio)
        precio = float(producto.precio_venta)
        margen_actual = producto.margen_actual
        margen_deseado = float(producto.margen_deseado or 0)
        
        # Calcular precio sugerido basado en margen deseado
        # Formula: Precio = Costo / (1 - Margen)
        precio_sugerido = None
        if margen_deseado > 0 and margen_deseado < 100:
            precio_sugerido = costo / (1 - (margen_deseado / 100))
        
        sugerencia_msg = f"\n\n💡 *Precio Sugerido:* ${precio_sugerido:.2f} (para margen del {margen_deseado}%)" if precio_sugerido else ""

        if precio < costo:
            ServicioAlertas.crear_alerta(
                tipo_alerta='MARGEN_BAJO',
                titulo=f"Pérdida Detectada: {producto.nombre}",
                mensaje=f"¡CRÍTICO! El precio de venta (${precio:.2f}) es menor al costo de adquisición (${costo:.2f}). Cada venta genera pérdidas.{sugerencia_msg}",
                prioridad='CRITICA',
                producto_id=producto.id,
                datos_adicionales={'precio_sugerido': precio_sugerido, 'costo': costo}
            )
        elif margen_actual < (margen_deseado * 0.3): # Menos del 30% del margen deseado (umbral de pánico)
             ServicioAlertas.crear_alerta(
                tipo_alerta='MARGEN_BAJO',
                titulo=f"Margen muy bajo: {producto.nombre}",
                mensaje=f"El margen actual ({margen_actual:.1f}%) está muy por debajo de tu objetivo ({margen_deseado:.1f}%). Revisa tus precios.{sugerencia_msg}",
                prioridad='ALTA',
                producto_id=producto.id,
                datos_adicionales={'precio_sugerido': precio_sugerido, 'costo': costo}
            )

    @staticmethod
    def verificar_y_alertar_vencimiento(lote_id):
        """Verifica si un lote está próximo a vencer y genera alerta."""
        from app.models import LoteProducto
        lote = LoteProducto.query.get(lote_id)
        if not lote or not lote.fecha_vencimiento:
            return
            
        dias = lote.dias_hasta_vencimiento
        if dias is not None:
            if dias <= 0:
                ServicioAlertas.crear_alerta(
                    tipo_alerta='VENCIMIENTO',
                    titulo=f"Producto Vencido: {lote.producto.nombre}",
                    mensaje=f"¡CRÍTICO! El lote {lote.numero_lote} de {lote.producto.nombre} venció el {lote.fecha_vencimiento.strftime('%d/%m/%Y')}. Retira el producto de la venta.",
                    prioridad='CRITICA',
                    producto_id=lote.producto_id,
                    datos_adicionales={'lote_id': lote.id, 'dias': dias}
                )
            elif dias <= 7:
                ServicioAlertas.crear_alerta(
                    tipo_alerta='VENCIMIENTO',
                    titulo=f"Próximo a Vencer: {lote.producto.nombre}",
                    mensaje=f"El lote {lote.numero_lote} de {lote.producto.nombre} vencerá en {dias} días ({lote.fecha_vencimiento.strftime('%d/%m/%Y')}).",
                    prioridad='ALTA',
                    producto_id=lote.producto_id,
                    datos_adicionales={'lote_id': lote.id, 'dias': dias}
                )
