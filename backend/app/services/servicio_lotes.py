"""
Servicio para la gestión inteligente de Lotes.
Implementa autogeneración y algoritmos FEFO/FIFO para despachos.
"""
from datetime import datetime
from app.core.extensions import db
from app.models import LoteProducto, Producto

class ServicioLotes:
    """Clase estática para manejar la lógica de extracción de lotes."""

    @staticmethod
    def autogenerar_numero_lote():
        """
        Genera un número de lote único basado en el timestamp actual.
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"LOTE-AUT-{timestamp}"

    @staticmethod
    def descontar_lotes_estrategicos(producto_id: int, cantidad_a_vender: float):
        """
        Aplica el algoritmo FEFO (First Expire, First Out) o FIFO (First In, First Out).
        Busca lotes activos del producto, los ordena por jerarquía de expiración o antigüedad,
        y resta a los lotes la cantidad indicada.
        
        Args:
            producto_id: ID del producto a descontar.
            cantidad_a_vender: Cantidad que está saliendo del inventario en total.
            
        Returns:
            lotes_afectados: dict con información de los lotes modificados, útil para auditoría o registro.
        """
        producto = Producto.query.get(producto_id)
        if not producto:
            return {}

        # Filtramos lotes activos que tengan saldo pendiente
        lotes_activos = LoteProducto.query.filter(
            LoteProducto.producto_id == producto_id,
            LoteProducto.cantidad_actual > 0,
            LoteProducto.esta_activo == True
        ).all()

        # Si no hay lotes, no hacemos descuento (se despacha mercancia 'suelta')
        if not lotes_activos:
            return {}

        # Ordenar lotes:
        # FEFO (Perecederos): Prioriza fecha_vencimiento ASC (los que vencen antes), si no hay fecha, manda al final.
        # FIFO (No Perecederos): Prioriza fecha_recepcion ASC (los mas antiguos).
        if producto.tiene_vencimiento:
            # Los que tienen fecha de vencimiento primero
            lotes_con_vencimiento = [l for l in lotes_activos if l.fecha_vencimiento is not None]
            lotes_sin_vencimiento = [l for l in lotes_activos if l.fecha_vencimiento is None]
            
            lotes_con_vencimiento.sort(key=lambda x: x.fecha_vencimiento)
            lotes_sin_vencimiento.sort(key=lambda x: x.fecha_recepcion)
            
            lotes_ordenados = lotes_con_vencimiento + lotes_sin_vencimiento
        else:
            # FIFO
            lotes_ordenados = sorted(lotes_activos, key=lambda x: x.fecha_recepcion)

        cantidad_restante = float(cantidad_a_vender)
        afectados = []

        for lote in lotes_ordenados:
            if cantidad_restante <= 0:
                break

            disponible_en_lote = float(lote.cantidad_actual)
            descontado = min(disponible_en_lote, cantidad_restante)
            
            # Aplicar descuento
            lote.cantidad_actual -= descontado
            cantidad_restante -= descontado
            
            afectados.append({
                'lote_id': lote.id,
                'numero_lote': lote.numero_lote,
                'cantidad_descontada': descontado,
                'restante_en_lote': float(lote.cantidad_actual)
            })

        # Registramos las persistencias en BD (el commit final ocurre en el router general)
        return afectados
