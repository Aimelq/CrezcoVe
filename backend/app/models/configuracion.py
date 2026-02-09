"""
Modelo de Configuración.
Almacena ajustes globales del sistema, como la tasa de cambio.
"""
from app.core.extensions import db
from app.models.base import ModeloBase

class Configuracion(ModeloBase):
    """Modelo para configuraciones del sistema."""
    
    __tablename__ = 'configuraciones'
    
    clave = db.Column(db.String(50), unique=True, nullable=False, index=True)
    valor = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    categoria = db.Column(db.String(50), nullable=True, default='GENERAL')
    
    @staticmethod
    def get_valor(clave, default=None):
        """Obtiene un valor de configuración por su clave."""
        config = Configuracion.query.filter_by(clave=clave).first()
        return config.valor if config else default
    
    @staticmethod
    def set_valor(clave, valor, descripcion=None, categoria='GENERAL'):
        """Establece o actualiza un valor de configuración."""
        config = Configuracion.query.filter_by(clave=clave).first()
        if config:
            config.valor = str(valor)
            if descripcion:
                config.descripcion = descripcion
        else:
            config = Configuracion(
                clave=clave, 
                valor=str(valor), 
                descripcion=descripcion,
                categoria=categoria
            )
            db.session.add(config)
        
        db.session.commit()
        return config

    def __repr__(self):
        return f'<Configuracion {self.clave}: {self.valor}>'
