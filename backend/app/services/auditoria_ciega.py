"""
Servicio de Auditoría Ciega.
Implementa el sistema anti-robo de auditorías aleatorias.
"""
import random
from datetime import datetime, timedelta
from app.core.extensions import db
from app.models import Producto, Alerta


class ServicioAuditoriaCiega:
    """Servicio para auditorías ciegas anti-robo."""
    
    @staticmethod
    def seleccionar_productos_auditoria(cantidad=2):
        """
        Selecciona productos aleatorios para auditoría.
        
        Args:
            cantidad: Número de productos a auditar
            
        Returns:
            Lista de productos seleccionados
        """
        # Obtener productos activos con stock
        productos_disponibles = Producto.query.filter(
            Producto.esta_activo == True,
            Producto.cantidad_actual > 0
        ).all()
        
        if len(productos_disponibles) < cantidad:
            cantidad = len(productos_disponibles)
        
        # Seleccionar aleatoriamente
        productos_seleccionados = random.sample(productos_disponibles, cantidad)
        
        return [
            {
                'id': p.id,
                'codigo_sku': p.codigo_sku,
                'nombre': p.nombre,
                'cantidad_sistema': p.cantidad_actual,
                'unidad_medida': p.unidad_medida
            }
            for p in productos_seleccionados
        ]
    
    @staticmethod
    def registrar_conteo_auditoria(producto_id, cantidad_fisica, usuario_id, notas=None):
        """
        Registra el conteo físico de una auditoría y compara con el sistema.
        
        Args:
            producto_id: ID del producto auditado
            cantidad_fisica: Cantidad contada físicamente
            usuario_id: ID del usuario que realizó el conteo
            notas: Notas adicionales
            
        Returns:
            dict con resultado de la auditoría
        """
        producto = Producto.query.get(producto_id)
        if not producto:
            raise ValueError(f'Producto con ID {producto_id} no encontrado')
        
        cantidad_sistema = producto.cantidad_actual
        discrepancia = cantidad_fisica - cantidad_sistema
        discrepancia_porcentaje = 0
        
        if cantidad_sistema > 0:
            discrepancia_porcentaje = (abs(discrepancia) / cantidad_sistema) * 100
        
        # Obtener umbral de discrepancia de configuración (default 5%)
        from flask import current_app
        umbral = current_app.config.get('PORCENTAJE_DISCREPANCIA_AUDITORIA', 5)
        
        hay_discrepancia_significativa = discrepancia_porcentaje > umbral
        
        # Si hay discrepancia significativa, crear alerta
        if hay_discrepancia_significativa:
            alerta = Alerta(
                producto_id=producto_id,
                tipo_alerta='DISCREPANCIA_AUDITORIA',
                titulo=f'Discrepancia en auditoría: {producto.nombre}',
                mensaje=f'Se encontró una discrepancia del {discrepancia_porcentaje:.1f}% en el producto {producto.nombre}. '
                       f'Sistema: {cantidad_sistema}, Físico: {cantidad_fisica}, Diferencia: {discrepancia}',
                prioridad='ALTA' if discrepancia_porcentaje > 10 else 'MEDIA',
                datos_adicionales={
                    'cantidad_sistema': cantidad_sistema,
                    'cantidad_fisica': cantidad_fisica,
                    'discrepancia': discrepancia,
                    'discrepancia_porcentaje': discrepancia_porcentaje,
                    'usuario_id': usuario_id,
                    'notas': notas
                }
            )
            db.session.add(alerta)
            db.session.commit()
        
        return {
            'producto_id': producto_id,
            'producto_nombre': producto.nombre,
            'cantidad_sistema': cantidad_sistema,
            'cantidad_fisica': cantidad_fisica,
            'discrepancia': discrepancia,
            'discrepancia_porcentaje': round(discrepancia_porcentaje, 2),
            'hay_discrepancia_significativa': hay_discrepancia_significativa,
            'umbral_porcentaje': umbral,
            'alerta_creada': hay_discrepancia_significativa,
            'fecha_auditoria': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def obtener_estadisticas_auditorias(dias=30):
        """
        Obtiene estadísticas de auditorías realizadas.
        
        Args:
            dias: Días hacia atrás para analizar
            
        Returns:
            dict con estadísticas
        """
        fecha_limite = datetime.utcnow() - timedelta(days=dias)
        
        alertas_auditoria = Alerta.query.filter(
            Alerta.tipo_alerta == 'DISCREPANCIA_AUDITORIA',
            Alerta.creado_en >= fecha_limite
        ).all()
        
        total_auditorias = len(alertas_auditoria)
        auditorias_con_discrepancia = sum(1 for a in alertas_auditoria if not a.esta_resuelta)
        
        return {
            'periodo_dias': dias,
            'total_auditorias': total_auditorias,
            'auditorias_con_discrepancia': auditorias_con_discrepancia,
            'tasa_discrepancia_porcentaje': round(
                (auditorias_con_discrepancia / total_auditorias * 100) if total_auditorias > 0 else 0,
                2
            )
        }
