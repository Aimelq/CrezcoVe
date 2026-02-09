"""
Inicialización de modelos.
Importa todos los modelos para que SQLAlchemy los reconozca.
"""
from app.models.base import ModeloBase
from app.models.configuracion import Configuracion
from app.models.usuario import Usuario
from app.models.producto import Producto, Categoria
from app.models.movimiento import MovimientoInventario
from app.models.lote import LoteProducto
from app.models.proveedor import Proveedor, proveedor_producto
from app.models.alerta import Alerta
from app.models.auditoria_log import AuditoriaLog

__all__ = [
    'ModeloBase',
    'Configuracion',
    'Usuario',
    'Producto',
    'Categoria',
    'MovimientoInventario',
    'LoteProducto',
    'Proveedor',
    'proveedor_producto',
    'Alerta',
    'AuditoriaLog'
]
