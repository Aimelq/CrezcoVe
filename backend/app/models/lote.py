"""
Modelo de Lotes de Producto.
Gestiona control de vencimientos y trazabilidad.
"""
from datetime import datetime, timedelta
from app.core.extensions import db
from app.models.base import ModeloBase


class LoteProducto(ModeloBase):
    """Modelo de lotes de productos."""
    
    __tablename__ = 'lotes_producto'
    
    # Relaciones
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False, index=True)
    
    # Información del lote
    numero_lote = db.Column(db.String(50), nullable=False, index=True)
    fecha_vencimiento = db.Column(db.Date, nullable=True, index=True)
    fecha_recepcion = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    
    # Cantidades
    cantidad_inicial = db.Column(db.Float, nullable=False)
    cantidad_actual = db.Column(db.Float, nullable=False)
    
    # Costos
    costo_lote = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Proveedor
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=True)
    
    # Notas
    notas = db.Column(db.Text, nullable=True)
    
    @property
    def esta_vencido(self):
        """Verifica si el lote está vencido."""
        if not self.fecha_vencimiento:
            return False
        return datetime.now().date() > self.fecha_vencimiento
    
    @property
    def dias_hasta_vencimiento(self):
        """Calcula días hasta el vencimiento."""
        if not self.fecha_vencimiento:
            return None
        delta = self.fecha_vencimiento - datetime.now().date()
        return delta.days
    
    @property
    def proximo_a_vencer(self):
        """Verifica si está próximo a vencer (menos de 7 días)."""
        dias = self.dias_hasta_vencimiento
        return dias is not None and 0 < dias <= 7
    
    def to_dict(self):
        """Convierte a diccionario con propiedades calculadas."""
        data = super().to_dict()
        data['esta_vencido'] = self.esta_vencido
        data['dias_hasta_vencimiento'] = self.dias_hasta_vencimiento
        data['proximo_a_vencer'] = self.proximo_a_vencer
        data['costo_lote'] = float(self.costo_lote)
        if self.fecha_vencimiento:
            data['fecha_vencimiento'] = self.fecha_vencimiento.isoformat()
        if self.fecha_recepcion:
            data['fecha_recepcion'] = self.fecha_recepcion.isoformat()
        return data
    
    def __repr__(self):
        return f'<LoteProducto {self.numero_lote} - Producto {self.producto_id}>'
