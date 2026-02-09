"""
Tareas de Celery para automatizaciones.
"""
from datetime import datetime, timedelta
from celery import Celery
from app.core.extensions import db
from app.models import Producto, MovimientoInventario, Alerta
from app.services.notificaciones_telegram import servicio_telegram
from app.services.prediccion_agotamiento import ServicioPrediccion
from app.services.auditoria_ciega import ServicioAuditoriaCiega
import os

# Configurar Celery
celery_app = Celery(
    'inventario_tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)


@celery_app.task
def verificar_stock_bajo():
    """
    Tarea periódica: Verifica productos con stock bajo y envía alertas.
    Ejecutar cada hora.
    """
    productos_bajo_stock = Producto.query.filter(
        Producto.esta_activo == True,
        Producto.cantidad_actual <= Producto.stock_minimo,
        Producto.alerta_stock_bajo_notificada == False
    ).all()
    
    for producto in productos_bajo_stock:
        # Crear alerta
        alerta = Alerta(
            producto_id=producto.id,
            tipo_alerta='STOCK_BAJO',
            titulo=f'Stock bajo: {producto.nombre}',
            mensaje=f'El producto {producto.nombre} tiene stock bajo ({producto.cantidad_actual} unidades)',
            prioridad='ALTA'
        )
        db.session.add(alerta)
        
        # Enviar notificación de Telegram
        servicio_telegram.notificar_stock_bajo(
            producto.nombre,
            producto.cantidad_actual,
            producto.stock_minimo
        )
        
        # Marcar como notificado
        producto.alerta_stock_bajo_notificada = True
    
    db.session.commit()
    return f"Verificados {len(productos_bajo_stock)} productos con stock bajo"


@celery_app.task
def verificar_productos_criticos():
    """
    Tarea periódica: Verifica productos críticos por agotarse.
    Ejecutar cada 6 horas.
    """
    productos_criticos = ServicioPrediccion.obtener_productos_criticos(limite=20)
    
    notificaciones_enviadas = 0
    
    for producto_data in productos_criticos:
        if producto_data.get('nivel_urgencia') in ['AGOTADO', 'CRITICO', 'URGENTE']:
            # 1. Crear alerta en base de datos si no existe una activa igual
            alerta_existente = Alerta.query.filter_by(
                producto_id=producto_data['producto_id'],
                tipo_alerta='STOCK_CRITICO',
                esta_resuelta=False
            ).first()
            
            if not alerta_existente:
                nueva_alerta = Alerta(
                    producto_id=producto_data['producto_id'],
                    tipo_alerta='STOCK_CRITICO',
                    titulo=f"Nivel {producto_data['nivel_urgencia']}: {producto_data['producto_nombre']}",
                    mensaje=f"El producto está en nivel {producto_data['nivel_urgencia']}. Stock: {producto_data['stock_actual']}. Sugerencia: Pedir {producto_data['cantidad_sugerida_pedido']} unidades.",
                    prioridad='CRITICA' if producto_data['nivel_urgencia'] == 'AGOTADO' else 'ALTA'
                )
                db.session.add(nueva_alerta)
            
            # 2. Notificar por Telegram
            servicio_telegram.notificar_producto_agotado(
                producto_data['producto_nombre'],
                int(producto_data.get('dias_hasta_agotar', 0) or 0)
            )
            notificaciones_enviadas += 1
    
    db.session.commit()
    return f"Enviadas {notificaciones_enviadas} notificaciones de productos críticos"


@celery_app.task
def generar_auditoria_ciega():
    """
    Tarea periódica: Genera auditoría ciega aleatoria.
    Ejecutar de lunes a viernes a las 10:00 AM.
    """
    productos = ServicioAuditoriaCiega.seleccionar_productos_auditoria(cantidad=2)
    
    # Enviar notificación con productos a auditar
    mensaje = "🔍 *Auditoría Ciega del Día*\n\n"
    mensaje += "Productos a contar:\n\n"
    
    for p in productos:
        mensaje += f"• *{p['nombre']}*\n"
        mensaje += f"  SKU: `{p['codigo_sku']}`\n"
        mensaje += f"  Ubicación: {p.get('ubicacion', 'N/A')}\n\n"
    
    mensaje += "_Registra el conteo físico en el sistema._"
    
    servicio_telegram.enviar_mensaje(mensaje)
    
    return f"Auditoría ciega generada con {len(productos)} productos"


@celery_app.task
def enviar_reporte_diario():
    """
    Tarea periódica: Envía reporte diario de cierre.
    Ejecutar todos los días a las 21:00.
    """
    hoy_inicio = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Calcular ventas del día
    ventas = MovimientoInventario.query.filter(
        MovimientoInventario.tipo_movimiento == 'VENTA',
        MovimientoInventario.fecha_movimiento >= hoy_inicio
    ).all()
    
    total_ventas = sum(v.precio_total for v in ventas if v.precio_total) or 0
    total_costo = sum(v.costo_total for v in ventas if v.costo_total) or 0
    ganancia = total_ventas - total_costo
    
    # Productos críticos
    productos_criticos = len(ServicioPrediccion.obtener_productos_criticos(limite=100))
    
    # Alertas activas
    alertas_activas = Alerta.query.filter_by(
        esta_resuelta=False,
        esta_activo=True
    ).count()
    
    # Enviar reporte
    servicio_telegram.enviar_reporte_diario(
        total_ventas,
        ganancia,
        productos_criticos,
        alertas_activas
    )
    
    return "Reporte diario enviado"


@celery_app.task
def limpiar_alertas_antiguas():
    """
    Tarea periódica: Limpia alertas resueltas antiguas.
    Ejecutar semanalmente.
    """
    fecha_limite = datetime.utcnow() - timedelta(days=30)
    
    alertas_antiguas = Alerta.query.filter(
        Alerta.esta_resuelta == True,
        Alerta.fecha_resolucion < fecha_limite
    ).all()
    
    for alerta in alertas_antiguas:
        alerta.esta_activo = False
    
    db.session.commit()
    
    return f"Limpiadas {len(alertas_antiguas)} alertas antiguas"


@celery_app.task
def verificar_dinero_dormido():
    """
    Tarea periódica: Verifica productos sin movimiento y genera alertas.
    Ejecutar semanalmente.
    """
    from app.services.dinero_dormido import ServicioDineroDormido
    reporte = ServicioDineroDormido.calcular_total_dinero_dormido(dias_sin_movimiento=60)
    
    alertas_creadas = 0
    for p_data in reporte.get('productos', []):
        # Solo alertar si el valor es significativo o lleva mucho tiempo
        if p_data['valor_inmovilizado'] > 50 or (p_data['dias_sin_venta'] and p_data['dias_sin_venta'] > 120):
            alerta_existente = Alerta.query.filter_by(
                producto_id=p_data['producto_id'],
                tipo_alerta='SIN_MOVIMIENTO',
                esta_resuelta=False
            ).first()
            
            if not alerta_existente:
                alerta = Alerta(
                    producto_id=p_data['producto_id'],
                    tipo_alerta='SIN_MOVIMIENTO',
                    titulo=f"Dinero Dormido: {p_data['nombre']}",
                    mensaje=f"El producto lleva {p_data['dias_sin_venta']} días sin ventas. "
                           f"Hay ${p_data['valor_inmovilizado']:.2f} inmovilizados. "
                           f"Sugerencia: Aplicar descuento del {p_data['descuento_sugerido_porcentaje']}%",
                    prioridad='BAJA' if p_data['valor_inmovilizado'] < 200 else 'MEDIA'
                )
                db.session.add(alerta)
                alertas_creadas += 1
    
    db.session.commit()
    return f"Generadas {alertas_creadas} alertas de dinero dormido"


@celery_app.task
def enviar_reporte_semanal_ai():
    """
    Tarea periódica: Envía reporte estratégico semanal generado por IA/BI.
    Ejecutar todos los lunes a las 08:00 VET (12:00 UTC).
    """
    from app.services.inteligencia_negocio import ServicioInteligenciaNegocio
    insights = ServicioInteligenciaNegocio.generar_insights_semanales()
    
    # Enviar a Telegram al dueño
    servicio_telegram.enviar_mensaje(insights['insights_narrativos'])
    
    return "Reporte semanal AI Insights enviado"


# Configuración de tareas periódicas
celery_app.conf.beat_schedule = {
    'verificar-stock-bajo-cada-hora': {
        'task': 'app.tasks.celery_tasks.verificar_stock_bajo',
        'schedule': 3600.0,  # Cada hora
    },
    'verificar-productos-criticos': {
        'task': 'app.tasks.celery_tasks.verificar_productos_criticos',
        'schedule': 21600.0,  # Cada 6 horas
    },
    'verificar-dinero-dormido-semanal': {
        'task': 'app.tasks.celery_tasks.verificar_dinero_dormido',
        'schedule': {
            'hour': 3,
            'minute': 0,
            'day_of_week': 1  # Lunes
        }
    },
    'reporte-semanal-ai-insights': {
        'task': 'app.tasks.celery_tasks.enviar_reporte_semanal_ai',
        'schedule': {
            'hour': 12,
            'minute': 0,
            'day_of_week': 1  # Lunes
        }
    },
    'auditoria-ciega-diaria': {
        'task': 'app.tasks.celery_tasks.generar_auditoria_ciega',
        'schedule': {
            'hour': 10,
            'minute': 0,
            'day_of_week': '1-5'  # Lunes a viernes
        }
    },
    'reporte-diario': {
        'task': 'app.tasks.celery_tasks.enviar_reporte_diario',
        'schedule': {
            'hour': 21,
            'minute': 0
        }
    },
    'limpiar-alertas-semanalmente': {
        'task': 'app.tasks.celery_tasks.limpiar_alertas_antiguas',
        'schedule': {
            'hour': 2,
            'minute': 0,
            'day_of_week': 0  # Domingo
        }
    },
}

celery_app.conf.timezone = 'UTC'
