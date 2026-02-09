"""
Modelo de Alertas.
Gestiona notificaciones y alertas del sistema.
"""
from app.core.extensions import db
from app.models.base import ModeloBase


class Alerta(ModeloBase):
    """Modelo de alertas del sistema."""
    
    __tablename__ = 'alertas'
    
    # Relaciones
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=True, index=True)
    
    # Tipo de alerta
    tipo_alerta = db.Column(
        db.String(30), 
        nullable=False, 
        index=True
    )  # STOCK_BAJO, VENCIMIENTO, SIN_MOVIMIENTO, DISCREPANCIA_AUDITORIA, MARGEN_BAJO
    
    # Contenido
    titulo = db.Column(db.String(200), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    
    # Prioridad
    prioridad = db.Column(
        db.String(10), 
        nullable=False, 
        default='MEDIA'
    )  # BAJA, MEDIA, ALTA, CRITICA
    
    # Estado
    esta_resuelta = db.Column(db.Boolean, nullable=False, default=False, index=True)
    fecha_resolucion = db.Column(db.DateTime, nullable=True)
    resuelta_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    notas_resolucion = db.Column(db.Text, nullable=True)
    
    # Notificación
    notificada = db.Column(db.Boolean, nullable=False, default=False)
    fecha_notificacion = db.Column(db.DateTime, nullable=True)
    
    # Metadatos adicionales (JSON)
    datos_adicionales = db.Column(db.JSON, nullable=True)
    
    # Relaciones
    resuelto_por = db.relationship('Usuario', foreign_keys=[resuelta_por_id])
    
    def marcar_como_resuelta(self, usuario_id, notas=None):
        """Marca la alerta como resuelta."""
        from datetime import datetime
        self.esta_resuelta = True
        self.fecha_resolucion = datetime.utcnow()
        self.resuelta_por_id = usuario_id
        if notas:
            self.notas_resolucion = notas
    
    def to_dict(self):
        """Convierte a diccionario."""
        data = super().to_dict()
        if self.fecha_resolucion:
            data['fecha_resolucion'] = self.fecha_resolucion.isoformat()
        if self.fecha_notificacion:
            data['fecha_notificacion'] = self.fecha_notificacion.isoformat()
        return data
    
    def __repr__(self):
        return f'<Alerta {self.tipo_alerta} - {self.titulo}>'
