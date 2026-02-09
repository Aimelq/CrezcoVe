"""
Modelo de Usuario.
Gestiona autenticación y roles del sistema.
"""
from app.core.extensions import db
from app.models.base import ModeloBase
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(ModeloBase):
    """Modelo de usuarios del sistema."""
    
    __tablename__ = 'usuarios'
    
    # Información básica
    nombre_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    telefono = db.Column(db.String(20), nullable=True)
    
    # Autenticación
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Rol: DUENO, EMPLEADO
    rol = db.Column(db.String(20), nullable=False, default='EMPLEADO', index=True)
    
    # Verificación
    email_verificado = db.Column(db.Boolean, default=False)
    token_verificacion = db.Column(db.String(100), nullable=True, unique=True)
    
    # Telegram
    telegram_chat_id = db.Column(db.String(50), nullable=True, unique=True)
    
    # Relaciones
    movimientos_creados = db.relationship('MovimientoInventario', backref='usuario_creador', lazy='dynamic')
    
    def establecer_password(self, password):
        """Hashea y guarda el password."""
        self.password_hash = generate_password_hash(password)
    
    def verificar_password(self, password):
        """Verifica si el password es correcto."""
        return check_password_hash(self.password_hash, password)
    
    def es_dueno(self):
        """Verifica si el usuario es dueño."""
        return self.rol == 'DUENO'
    
    def to_dict(self):
        """Convierte a diccionario sin incluir el password."""
        data = super().to_dict()
        data.pop('password_hash', None)
        return data
    
    def __repr__(self):
        return f'<Usuario {self.email} - {self.rol}>'
