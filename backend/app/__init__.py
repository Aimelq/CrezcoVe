"""
Factory de aplicación Flask.
Crea y configura la aplicación con todas sus extensiones.
"""
import os
from flask import Flask
from app.core.config import obtener_configuracion
from app.core.extensions import init_extensions


def create_app(config_name=None):
    """
    Crea y configura la aplicación Flask.
    
    Args:
        config_name: Nombre de la configuración a usar (development, production, testing)
        
    Returns:
        Aplicación Flask configurada
    """
    app = Flask(__name__)
    
    # Cargar configuración
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    config_class = obtener_configuracion(config_name)
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    init_extensions(app)
    
    # Registrar blueprints/namespaces
    registrar_blueprints(app)
    
    # Registrar middleware
    registrar_middleware(app)
    
    # Registrar comandos CLI
    registrar_comandos(app)
    
    # Manejadores de errores
    registrar_manejadores_errores(app)
    
    return app


def registrar_blueprints(app):
    """Registra todos los blueprints de la API."""
    from app.api.v1.auth.routes import auth_ns
    from app.api.v1.productos.routes import productos_ns
    from app.api.v1.inventario.routes import inventario_ns
    from app.api.v1.proveedores.routes import proveedores_ns
    from app.api.v1.reportes.routes import reportes_ns
    from app.api.v1.usuarios.routes import usuarios_ns
    from app.api.v1.alertas.routes import alertas_ns
    from app.api.v1.lotes.routes import lotes_ns
    from app.api.v1.inteligencia.routes import inteligencia_ns
    
    from flask_restx import Api
    
    # Crear API con documentación Swagger en español
    api = Api(
        app,
        version='1.0',
        title='API de Inventario Inteligente',
        description='Sistema completo de gestión de inventario para PYMEs',
        doc='/api/docs',
        prefix='/api'
    )
    
    # Registrar namespaces
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(productos_ns, path='/productos')
    api.add_namespace(inventario_ns, path='/inventario')
    api.add_namespace(proveedores_ns, path='/proveedores')
    api.add_namespace(reportes_ns, path='/reportes')
    api.add_namespace(usuarios_ns, path='/usuarios')
    api.add_namespace(alertas_ns, path='/alertas')
    api.add_namespace(lotes_ns, path='/lotes')
    api.add_namespace(inteligencia_ns, path='/inteligencia')
    
    # Registrar blueprints standard (setup)
    from app.api.v1.setup.routes import bp as setup_bp
    app.register_blueprint(setup_bp)

    # Registrar blueprints de sistema (backup, etc)
    from app.api.v1.system.routes import bp as system_bp
    app.register_blueprint(system_bp)


def registrar_middleware(app):
    """Registra middleware personalizado."""
    from app.middleware.audit_middleware import AuditoriaMiddleware
    
    app.wsgi_app = AuditoriaMiddleware(app.wsgi_app)


def registrar_comandos(app):
    """Registra comandos CLI personalizados."""
    from app.core.extensions import db
    from app.models import Usuario, Categoria
    
    @app.cli.command('init-db')
    def init_db():
        """Inicializa la base de datos."""
        db.create_all()
        print('✅ Base de datos inicializada')
    
    @app.cli.command('seed-data')
    def seed_data():
        """Carga datos iniciales."""
        # Crear categorías por defecto
        categorias_default = [
            {'nombre': 'Alimentos', 'icono': 'utensils'},
            {'nombre': 'Bebidas', 'icono': 'coffee'},
            {'nombre': 'Limpieza', 'icono': 'spray-can'},
            {'nombre': 'Electrónicos', 'icono': 'laptop'},
            {'nombre': 'Ropa', 'icono': 'shirt'},
            {'nombre': 'Otros', 'icono': 'box'}
        ]
        
        for cat_data in categorias_default:
            if not Categoria.query.filter_by(nombre=cat_data['nombre']).first():
                categoria = Categoria(**cat_data)
                db.session.add(categoria)
        
        # Crear usuario administrador por defecto
        if not Usuario.query.filter_by(email='admin@inventario.com').first():
            admin = Usuario(
                nombre_completo='Administrador',
                email='admin@inventario.com',
                rol='DUENO'
            )
            admin.establecer_password('admin123')
            db.session.add(admin)
        
        db.session.commit()
        print('✅ Datos iniciales cargados')


def registrar_manejadores_errores(app):
    """Registra manejadores de errores personalizados."""
    from flask import jsonify
    from werkzeug.exceptions import HTTPException
    
    @app.errorhandler(HTTPException)
    def manejar_error_http(error):
        """Maneja errores HTTP."""
        respuesta = {
            'error': error.name,
            'mensaje': error.description,
            'codigo': error.code
        }
        return jsonify(respuesta), error.code
    
    @app.errorhandler(Exception)
    def manejar_error_general(error):
        """Maneja errores generales."""
        app.logger.error(f'Error no manejado: {str(error)}')
        respuesta = {
            'error': 'Error interno del servidor',
            'mensaje': 'Ocurrió un error inesperado. Por favor contacte al administrador.',
            'codigo': 500
        }
        return jsonify(respuesta), 500
