"""
Modelo de Proveedores.
Gestiona información de proveedores y relaciones con productos.
"""
from app.core.extensions import db
from app.models.base import ModeloBase


# Tabla de asociación muchos-a-muchos entre proveedores y productos
proveedor_producto = db.Table(
    'proveedor_producto',
    db.Column('proveedor_id', db.Integer, db.ForeignKey('proveedores.id'), primary_key=True),
    db.Column('producto_id', db.Integer, db.ForeignKey('productos.id'), primary_key=True),
    db.Column('precio_compra_habitual', db.Numeric(10, 2), nullable=True),
    db.Column('tiempo_entrega_dias', db.Integer, nullable=True),
    db.Column('es_proveedor_principal', db.Boolean, default=False)
)


class Proveedor(ModeloBase):
    """Modelo de proveedores."""
    
    __tablename__ = 'proveedores'
    
    # Información básica
    nombre = db.Column(db.String(200), nullable=False, index=True)
    nombre_contacto = db.Column(db.String(100), nullable=True)
    
    # Contacto
    telefono = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    direccion = db.Column(db.Text, nullable=True)
    
    # Información comercial
    rif = db.Column(db.String(20), nullable=True, unique=True)  # RIF (Venezuela)
    terminos_pago = db.Column(db.String(100), nullable=True)  # Ej: "30 días", "Contado"
    
    # Calificación
    calificacion = db.Column(db.Float, nullable=True)  # 1-5 estrellas
    
    # Notas
    notas = db.Column(db.Text, nullable=True)
    
    # Relaciones
    productos = db.relationship(
        'Producto',
        secondary=proveedor_producto,
        backref=db.backref('proveedores', lazy='dynamic')
    )
    lotes = db.relationship('LoteProducto', backref='proveedor', lazy='dynamic')
    movimientos = db.relationship('MovimientoInventario', backref='proveedor', lazy='dynamic')
    
    def to_dict(self):
        """Convierte a diccionario."""
        data = super().to_dict()
        data['cantidad_productos'] = len(self.productos)
        return data
    
    def __repr__(self):
        return f'<Proveedor {self.nombre}>'
