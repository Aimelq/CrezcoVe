"""
Servicio de Inteligencia de Negocio.
Agrega métricas financieras y genera reportes estratégicos (AI Insights).
"""
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func
from app.core.extensions import db
from app.models import Producto, MovimientoInventario, Proveedor
from app.services.dinero_dormido import ServicioDineroDormido
from app.services.prediccion_agotamiento import ServicioPrediccion
from app.services.asistente_precios import AsistentePrecios

class ServicioInteligenciaNegocio:
    """Servicio para análisis avanzado de negocio."""

    @staticmethod
    def obtener_resumen_salud_financiera():
        """Obtiene métricas clave de la salud del negocio."""
        # 1. Valor total del inventario
        productos_activos = Producto.query.filter_by(esta_activo=True).all()
        valor_total_inventario = sum(p.valor_inventario for p in productos_activos)
        
        # 2. Dinero Dormido (+60 días sin ventas)
        resumen_dormido = ServicioDineroDormido.calcular_total_dinero_dormido(dias_sin_movimiento=60)
        valor_dormido = resumen_dormido['valor_total_inmovilizado']
        
        # 3. Margen promedio y salud de márgenes
        margenes = [p.margen_actual for p in productos_activos if p.costo_promedio > 0]
        margen_promedio = sum(margenes) / len(margenes) if margenes else 0
        
        productos_bajo_margen = sum(1 for p in productos_activos if p.margen_actual < p.margen_deseado)
        
        # 4. Ventas del último mes vs anterior (tendencia)
        hace_30_dias = datetime.utcnow() - timedelta(days=30)
        hace_60_dias = datetime.utcnow() - timedelta(days=60)
        
        ventas_mes_actual = db.session.query(func.sum(MovimientoInventario.precio_total)).filter(
            MovimientoInventario.tipo_movimiento == 'VENTA',
            MovimientoInventario.fecha_movimiento >= hace_30_dias
        ).scalar() or 0
        
        ventas_mes_anterior = db.session.query(func.sum(MovimientoInventario.precio_total)).filter(
            MovimientoInventario.tipo_movimiento == 'VENTA',
            MovimientoInventario.fecha_movimiento >= hace_60_dias,
            MovimientoInventario.fecha_movimiento < hace_30_dias
        ).scalar() or 0
        
        tendencia_ventas = 0
        if ventas_mes_anterior > 0:
            tendencia_ventas = ((float(ventas_mes_actual) - float(ventas_mes_anterior)) / float(ventas_mes_anterior)) * 100

        return {
            'valor_total_inventario': round(float(valor_total_inventario), 2),
            'dinero_dormido': round(float(valor_dormido), 2),
            'porcentaje_dormido': round((valor_dormido / valor_total_inventario * 100), 1) if valor_total_inventario > 0 else 0,
            'margen_promedio': round(margen_promedio, 1),
            'productos_bajo_margen': productos_bajo_margen,
            'ventas_mes_actual': round(float(ventas_mes_actual), 2),
            'tendencia_ventas_porcentaje': round(tendencia_ventas, 1),
            'productos_dormidos_top': resumen_dormido['productos'][:5]
        }

    @staticmethod
    def generar_insights_semanales():
        """Genera un reporte narrativo con sugerencias estratégicas."""
        hace_7_dias = datetime.utcnow() - timedelta(days=7)
        
        # 1. Producto Estrella (más vendido en volumen)
        producto_estrella_data = db.session.query(
            MovimientoInventario.producto_id,
            func.sum(func.abs(MovimientoInventario.cantidad)).label('total_vendido')
        ).filter(
            MovimientoInventario.tipo_movimiento == 'VENTA',
            MovimientoInventario.fecha_movimiento >= hace_7_dias
        ).group_by(MovimientoInventario.producto_id).order_by(db.desc('total_vendido')).first()
        
        producto_estrella = None
        if producto_estrella_data:
            producto_estrella = Producto.query.get(producto_estrella_data.producto_id)

        # 2. Análisis de Inflación y Proveedores
        # Buscamos productos cuyo último costo subió > 5% respecto al promedio histórico
        productos_inflacion = []
        for p in Producto.query.filter(Producto.esta_activo == True, Producto.ultimo_costo_compra > 0).all():
            if p.costo_promedio > 0:
                variacion = ((float(p.ultimo_costo_compra) - float(p.costo_promedio)) / float(p.costo_promedio)) * 100
                if variacion > 5:
                    # Buscar proveedores alternativos que también vendan este producto
                    alternativos = [prov.nombre for prov in p.proveedores if prov.id != p.lotes.order_by(db.desc('id')).first().proveedor_id] if p.lotes.count() > 0 else []
                    productos_inflacion.append({
                        'nombre': p.nombre,
                        'variacion': variacion,
                        'margen_caida': p.margen_deseado - p.margen_actual,
                        'alternativos': alternativos[:2]
                    })
        
        # 3. Salud General
        resumen = ServicioInteligenciaNegocio.obtener_resumen_salud_financiera()
        
        # Construir el mensaje para Telegram
        mensaje = f"🧠 *AI INSIGHTS SEMANALES*\n_{datetime.now().strftime('%d/%m/%Y')}_\n\n"
        
        if producto_estrella:
            mensaje += f"🏆 *Producto Estrella:* {producto_estrella.nombre}\n"
            mensaje += f"   Vendiste {producto_estrella_data.total_vendido} unidades esta semana. ¡Sigue así!\n\n"
        
        mensaje += "💰 *Salud Financiera:*\n"
        mensaje += f"• Valor Inventario: ${resumen['valor_total_inventario']:.2f}\n"
        mensaje += f"• Dinero Dormido: ${resumen['dinero_dormido']:.2f} ({resumen['porcentaje_dormido']}%)\n"
        if resumen['tendencia_ventas_porcentaje'] > 0:
            mensaje += f"• Tendencia Ventas: 📈 +{resumen['tendencia_ventas_porcentaje']}%\n"
        else:
            mensaje += f"• Tendencia Ventas: 📉 {resumen['tendencia_ventas_porcentaje']}%\n"
        
        if productos_inflacion:
            mensaje += "\n⚠️ *Alertas de Margen:*\n"
            for alert in productos_inflacion[:3]:
                mensaje += f"• *{alert['nombre']}*: Costo subió {alert['variacion']:.1f}%. "
                if alert['alternativos']:
                    mensaje += f"Sugerencia: Cotizar con {', '.join(alert['alternativos'])}.\n"
                else:
                    mensaje += "Sugerencia: Evaluar ajuste de precio.\n"
        
        if resumen['dinero_dormido'] > 0:
            mensaje += f"\n💡 *Recomendación:* Tienes {resumen['porcentaje_dormido']}% de tu capital estancado. Considera liquidar los productos del 'Top 5 Dormidos' para recuperar flujo de caja."

        return {
            'resumen': resumen,
            'insights_narrativos': mensaje,
            'alertas_inflacion': productos_inflacion
        }
