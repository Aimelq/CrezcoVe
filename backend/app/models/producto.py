"""
Modelo de Producto.
Gestiona el catálogo de productos del inventario.
"""
from app.core.extensions import db
from app.models.base import ModeloBase


class Producto(ModeloBase):
    """Modelo de productos."""
    
    __tablename__ = 'productos'
    
    # Identificación
    codigo_sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=True)
    
    # Categorización
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    unidad_medida = db.Column(db.String(20), nullable=False, default='UNIDAD')  # UNIDAD, KG, LITRO, CAJA, etc.
    
    # Control de stock
    cantidad_actual = db.Column(db.Float, nullable=False, default=0.0)
    stock_minimo = db.Column(db.Float, nullable=False, default=0.0)
    stock_maximo = db.Column(db.Float, nullable=True)
    umbral_alerta = db.Column(db.Float, nullable=True)  # Punto de reorden
    
    # Costos y precios
    costo_promedio = db.Column(db.Numeric(18, 6), nullable=False, default=0.0)
    ultimo_costo_compra = db.Column(db.Numeric(18, 6), nullable=True)
    precio_venta = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    margen_deseado = db.Column(db.Float, nullable=False, default=30.0)  # Porcentaje
    
    # Control de vencimiento
    tiene_vencimiento = db.Column(db.Boolean, nullable=False, default=False)
    dias_vencimiento = db.Column(db.Integer, nullable=True)  # Días típicos de vida útil
    
    # Alertas
    alerta_stock_bajo_notificada = db.Column(db.Boolean, nullable=False, default=False)
    
    # Fraccionamiento (Multi-unidades)
    producto_padre_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=True)
    factor_conversion = db.Column(db.Float, nullable=True, default=1.0) # Cuántos hijos salen de 1 padre
    
    # Información adicional
    imagen_url = db.Column(db.String(255), nullable=True)
    notas = db.Column(db.Text, nullable=True)
    
    # Relaciones
    categoria = db.relationship('Categoria', backref='productos')
    movimientos = db.relationship('MovimientoInventario', backref='producto', lazy='dynamic')
    lotes = db.relationship('LoteProducto', backref='producto', lazy='dynamic')
    alertas = db.relationship('Alerta', backref='producto', lazy='dynamic')
    
    # Relación jerárquica para fraccionamiento
    hijos = db.relationship('Producto', backref=db.backref('padre', remote_side='Producto.id'), lazy='dynamic')
    
    @property
    def esta_bajo_stock(self):
        """Verifica si el producto está bajo en stock."""
        return self.cantidad_actual <= self.stock_minimo
    
    @property
    def margen_actual(self):
        """Calcula el margen de ganancia actual."""
        if float(self.costo_promedio) == 0:
            return 0
        return ((float(self.precio_venta) - float(self.costo_promedio)) / float(self.costo_promedio)) * 100
    
    @property
    def valor_inventario(self):
        """Calcula el valor total del inventario de este producto."""
        return float(self.costo_promedio) * self.cantidad_actual
    
    def to_dict(self):
        """Convierte a diccionario con propiedades calculadas."""
        data = super().to_dict()
        data['esta_bajo_stock'] = self.esta_bajo_stock
        data['margen_actual'] = round(self.margen_actual, 2)
        data['valor_inventario'] = round(self.valor_inventario, 2)
        data['costo_promedio'] = float(self.costo_promedio)
        data['ultimo_costo_compra'] = float(self.ultimo_costo_compra) if self.ultimo_costo_compra else None
        data['precio_venta'] = float(self.precio_venta)
        
        # Costo de Referencia (Reposición): Prioriza el último costo para decisiones de precio
        costo_avg = float(self.costo_promedio)
        ultimo_costo = float(self.ultimo_costo_compra) if self.ultimo_costo_compra else 0
        data['costo_referencia'] = max(costo_avg, ultimo_costo) if ultimo_costo > 0 else costo_avg
        
        return data
    
    def soft_delete(self):
        """Sobrescribe soft_delete para desactivar también los lotes asociados y liberar el SKU."""
        import time
        self.esta_activo = False
        
        # Liberar el SKU renombrándolo con sufijo de timestamp
        # Ejemplo: "COCA-COLA" -> "COCA-COLA_DEL_1712345678"
        timestamp = int(time.time())
        self.codigo_sku = f"{self.codigo_sku}_DEL_{timestamp}"
        
        # Desactivar todos sus lotes para mantener coherencia en la DB
        for lote in self.lotes:
            lote.esta_activo = False
        db.session.commit()

    def __repr__(self):
        return f'<Producto {self.codigo_sku} - {self.nombre}>'


class Categoria(ModeloBase):
    """Modelo de categorías de productos."""
    
    __tablename__ = 'categorias'
    
    nombre = db.Column(db.String(100), nullable=False, unique=True, index=True)
    descripcion = db.Column(db.Text, nullable=True)
    icono = db.Column(db.String(50), nullable=True)  # Nombre del icono para UI
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'
