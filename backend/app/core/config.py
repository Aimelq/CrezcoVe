"""
Configuración de la aplicación Flask.
Todas las configuraciones están en español.
"""
import os
from datetime import timedelta


class ConfigBase:
    """Configuración base compartida por todos los entornos."""
    
    # Configuración general
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-secreta-cambiar-en-produccion')
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://usuario_inventario:password@localhost:5432/inventario_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secreto-cambiar-en-produccion')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID_DUENO = os.getenv('TELEGRAM_CHAT_ID_DUENO', '')
    TELEGRAM_CHAT_ID_EMPLEADOS = os.getenv('TELEGRAM_CHAT_ID_EMPLEADOS', '')
    
    # n8n
    N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook')
    
    # Configuración de negocio
    MARGEN_GANANCIA_DEFAULT = int(os.getenv('MARGEN_GANANCIA_DEFAULT', '30'))
    DIAS_ALERTA_VENCIMIENTO = int(os.getenv('DIAS_ALERTA_VENCIMIENTO', '7'))
    PORCENTAJE_DISCREPANCIA_AUDITORIA = int(os.getenv('PORCENTAJE_DISCREPANCIA_AUDITORIA', '5'))
    DIAS_SIN_MOVIMIENTO_DINERO_DORMIDO = int(os.getenv('DIAS_SIN_MOVIMIENTO_DINERO_DORMIDO', '60'))
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'xlsx', 'xls'}
    
    # Celery
    CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'America/Santo_Domingo'
    CELERY_ENABLE_UTC = True


class ConfigDesarrollo(ConfigBase):
    """Configuración para entorno de desarrollo."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True  # Mostrar queries SQL en desarrollo


class ConfigProduccion(ConfigBase):
    """Configuración para entorno de producción."""
    DEBUG = False
    TESTING = False
    
    # En producción, estas variables DEBEN estar definidas
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')


class ConfigPruebas(ConfigBase):
    """Configuración para pruebas."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Diccionario de configuraciones
configuraciones = {
    'development': ConfigDesarrollo,
    'production': ConfigProduccion,
    'testing': ConfigPruebas,
    'default': ConfigDesarrollo
}


def obtener_configuracion(nombre_entorno=None):
    """
    Obtiene la configuración según el entorno.
    
    Args:
        nombre_entorno: Nombre del entorno (development, production, testing)
        
    Returns:
        Clase de configuración correspondiente
    """
    if nombre_entorno is None:
        nombre_entorno = os.getenv('FLASK_ENV', 'development')
    
    return configuraciones.get(nombre_entorno, ConfigDesarrollo)
