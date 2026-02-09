"""
Extensiones de Flask inicializadas aquí para evitar importaciones circulares.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from redis import Redis

# Inicializar extensiones (sin app todavía)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()
cors = CORS()
redis_client = None  # Se inicializa en create_app


def init_extensions(app):
    """
    Inicializa todas las extensiones con la aplicación Flask.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Inicializar Redis
    global redis_client
    redis_client = Redis.from_url(
        app.config['REDIS_URL'],
        decode_responses=True
    )
    
    # Configurar JWT
    @jwt.token_in_blocklist_loader
    def verificar_token_revocado(jwt_header, jwt_payload):
        """Verifica si un token JWT ha sido revocado."""
        jti = jwt_payload["jti"]
        token_en_redis = redis_client.get(f"token_revocado:{jti}")
        return token_en_redis is not None

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        app.logger.warning(f"Token expirado: {jwt_payload}")
        return {"mensaje": "El token ha expirado", "error": "token_expired"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        app.logger.warning(f"Token inválido: {error}")
        return {"mensaje": f"Token inválido: {error}", "error": "invalid_token"}, 422

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        app.logger.warning(f"Token faltante: {error}")
        return {"mensaje": f"Acceso requerido: {error}", "error": "authorization_required"}, 401
