"""
Modelo de Movimientos de Inventario.
Registra todas las transacciones de entrada y salida.
"""
from app.core.extensions import db
from app.models.base import ModeloBase


class MovimientoInventario(ModeloBase):
    """Modelo de movimientos de inventario."""
    
    __tablename__ = 'movimientos_inventario'
    
    # Relaciones
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=True)
    lote_id = db.Column(db.Integer, db.ForeignKey('lotes_producto.id'), nullable=True)
    
    # Tipo de movimiento
    tipo_movimiento = db.Column(
        db.String(20), 
        nullable=False, 
        index=True
    )  # COMPRA, VENTA, AJUSTE, MERMA, TRANSFERENCIA, AUDITORIA
    
    # Cantidades
    cantidad = db.Column(db.Float, nullable=False)
    cantidad_anterior = db.Column(db.Float, nullable=True)  # Stock antes del movimiento
    cantidad_nueva = db.Column(db.Float, nullable=True)  # Stock después del movimiento
    
    # Costos (para compras y ajustes)
    costo_unitario = db.Column(db.Numeric(10, 2), nullable=True)
    costo_total = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Precios (para ventas)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=True)
    precio_total = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Motivo de ajuste (para AJUSTE y MERMA)
    motivo_ajuste = db.Column(
        db.String(30), 
        nullable=True
    )  # DETERIORADO, VENCIDO, USO_INTERNO, ROBO, OTRO
    
    # Referencias
    referencia_id = db.Column(db.String(50), nullable=True)  # Número de factura, orden, etc.
    notas = db.Column(db.Text, nullable=True)
    
    # Metadatos
    fecha_movimiento = db.Column(db.DateTime, nullable=False, index=True)
    
    @property
    def es_entrada(self):
        """Verifica si es un movimiento de entrada."""
        return self.tipo_movimiento in ['COMPRA', 'AJUSTE'] and self.cantidad > 0
    
    @property
    def es_salida(self):
        """Verifica si es un movimiento de salida."""
        return self.tipo_movimiento in ['VENTA', 'MERMA', 'AJUSTE'] and self.cantidad < 0
    
    @property
    def ganancia(self):
        """Calcula la ganancia en ventas."""
        if self.tipo_movimiento == 'VENTA' and self.precio_total and self.costo_total:
            return float(self.precio_total) - float(self.costo_total)
        return 0
    
    def to_dict(self):
        """Convierte a diccionario con propiedades calculadas."""
        data = super().to_dict()
        data['es_entrada'] = self.es_entrada
        data['es_salida'] = self.es_salida
        data['ganancia'] = round(self.ganancia, 2)
        
        # Convertir Decimal a float
        if self.costo_unitario:
            data['costo_unitario'] = float(self.costo_unitario)
        if self.costo_total:
            data['costo_total'] = float(self.costo_total)
        if self.precio_unitario:
            data['precio_unitario'] = float(self.precio_unitario)
        if self.precio_total:
            data['precio_total'] = float(self.precio_total)
        
        return data
    
    def __repr__(self):
        return f'<MovimientoInventario {self.tipo_movimiento} - Producto {self.producto_id}>'
