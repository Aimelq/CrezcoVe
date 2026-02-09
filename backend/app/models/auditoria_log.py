"""
Modelo de Auditoría (Logs de Seguridad).
Registra todas las acciones importantes del sistema - "Caja Negra".
"""
from app.core.extensions import db
from app.models.base import ModeloBase


class AuditoriaLog(ModeloBase):
    """Modelo de logs de auditoría."""
    
    __tablename__ = 'auditoria_logs'
    
    # Usuario que realizó la acción
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    
    # Acción realizada
    accion = db.Column(
        db.String(20), 
        nullable=False, 
        index=True
    )  # CREAR, ACTUALIZAR, ELIMINAR, LOGIN, LOGOUT
    
    # Tabla y registro afectado
    tabla_afectada = db.Column(db.String(50), nullable=False, index=True)
    registro_id = db.Column(db.Integer, nullable=True)
    
    # Valores antes y después (JSON)
    valores_anteriores = db.Column(db.JSON, nullable=True)
    valores_nuevos = db.Column(db.JSON, nullable=True)
    
    # Metadatos de la petición
    endpoint = db.Column(db.String(200), nullable=True)
    metodo_http = db.Column(db.String(10), nullable=True)
    direccion_ip = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # Timestamp
    fecha_hora = db.Column(db.DateTime, nullable=False, index=True)
    
    # Relaciones
    usuario = db.relationship('Usuario', backref='logs_auditoria')
    
    # Nota: Los logs de auditoría NO se pueden eliminar (no heredan soft_delete)
    # Por eso no usamos ModeloBase completo
    
    def __repr__(self):
        return f'<AuditoriaLog {self.accion} - {self.tabla_afectada} por Usuario {self.usuario_id}>'
