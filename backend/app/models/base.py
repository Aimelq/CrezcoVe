"""
Modelo base para todas las tablas.
Incluye campos comunes como timestamps y soft delete.
"""
from datetime import datetime
from app.core.extensions import db


class ModeloBase(db.Model):
    """Clase base abstracta para todos los modelos."""
    
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    esta_activo = db.Column(db.Boolean, nullable=False, default=True, index=True)
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        resultado = {}
        for columna in self.__table__.columns:
            valor = getattr(self, columna.name)
            if isinstance(valor, datetime):
                resultado[columna.name] = valor.isoformat()
            else:
                resultado[columna.name] = valor
        return resultado
    
    def soft_delete(self):
        """Marca el registro como inactivo en lugar de eliminarlo."""
        self.esta_activo = False
        db.session.commit()
    
    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'
