"""
Endpoints de Reportes.
Genera reportes y estadísticas del sistema.
"""
from datetime import datetime, timedelta
import io
import pandas as pd
from flask import request, send_file
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

@reportes_ns.route('/ventas/excel')
class ReporteVentasExcel(Resource):
    @jwt_required()
    def get(self):
        """Descarga reporte de ventas en Excel (Mensual o Diario)."""
        try:
            tipo = request.args.get('tipo', 'mensual') # 'mensual' o 'diario'
            
            if tipo == 'mensual':
                return self._reporte_mensual()
            elif tipo == 'diario':
                return self._reporte_diario()
            else:
                reportes_ns.abort(400, "Tipo de reporte no válido")

        except Exception as e:
            reportes_ns.abort(500, f"Error generando reporte: {str(e)}")

    def _reporte_mensual(self):
        mes = request.args.get('mes', type=int, default=datetime.now().month)
        anio = request.args.get('anio', type=int, default=datetime.now().year)

        fecha_inicio = datetime(anio, mes, 1, 0, 0, 0)
        if mes == 12:
            fecha_fin = datetime(anio + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
        else:
            fecha_fin = datetime(anio, mes + 1, 1, 0, 0, 0) - timedelta(seconds=1)

        # Agrupar ventas por día
        movimientos = db.session.query(
            func.date(MovimientoInventario.fecha_movimiento).label('fecha'),
            func.count(MovimientoInventario.id).label('cantidad_ventas'),
            func.sum(MovimientoInventario.precio_total).label('total_vendido')
        ).filter(
            MovimientoInventario.tipo_movimiento == 'VENTA',
            MovimientoInventario.fecha_movimiento >= fecha_inicio,
            MovimientoInventario.fecha_movimiento <= fecha_fin
        ).group_by(
            func.date(MovimientoInventario.fecha_movimiento)
        ).order_by(
            func.date(MovimientoInventario.fecha_movimiento)
        ).all()

        data = []
        for fecha, cantidad, total in movimientos:
            data.append({
                'Fecha': fecha.strftime('%Y-%m-%d'),
                'Cantidad Ventas': cantidad,
                'Total Vendido ($)': float(total or 0)
            })
        
        df = pd.DataFrame(data)
        
        if not df.empty:
            total_row = pd.DataFrame([{
                'Fecha': 'TOTALES',
                'Cantidad Ventas': df['Cantidad Ventas'].sum(),
                'Total Vendido ($)': df['Total Vendido ($)'].sum()
            }])
            df = pd.concat([df, total_row], ignore_index=True)

        return self._generar_excel(df, f"Ventas_Mensual_{mes:02d}_{anio}")

    def _reporte_diario(self):
        fecha_str = request.args.get('fecha') # YYYY-MM-DD
        if not fecha_str:
            reportes_ns.abort(400, "Fecha requerida para reporte diario")
            
        try:
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
            fecha_inicio = fecha_obj.replace(hour=0, minute=0, second=0)
            fecha_fin = fecha_obj.replace(hour=23, minute=59, second=59)
        except ValueError:
            reportes_ns.abort(400, "Formato de fecha inválido (YYYY-MM-DD)")

        # Consultar transacciones del día
        movimientos = MovimientoInventario.query.filter(
            MovimientoInventario.tipo_movimiento == 'VENTA',
            MovimientoInventario.fecha_movimiento >= fecha_inicio,
            MovimientoInventario.fecha_movimiento <= fecha_fin
        ).order_by(MovimientoInventario.fecha_movimiento).all()

        data = []
        for mov in movimientos:
            data.append({
                'Hora': mov.fecha_movimiento.strftime('%H:%M:%S'),
                'Referencia': mov.referencia_id or 'S/R',
                'Total Venta ($)': float(mov.precio_total or 0),
                'Notas': mov.notas or ''
            })

        df = pd.DataFrame(data)

        if not df.empty:
            total_row = pd.DataFrame([{
                'Hora': 'TOTAL',
                'Referencia': '',
                'Total Venta ($)': df['Total Venta ($)'].sum(),
                'Notas': ''
            }])
            df = pd.concat([df, total_row], ignore_index=True)

        return self._generar_excel(df, f"Ventas_Diario_{fecha_str}")

    def _generar_excel(self, df, filename):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            sheet_name = 'Reporte'
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                try:
                    max_length = max(len(str(cell.value)) for cell in column)
                    adjusted_width = (max_length + 2)
                    worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
                except:
                    pass
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"{filename}.xlsx"
        )
