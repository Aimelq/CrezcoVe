from flask import Blueprint, jsonify, current_app
import subprocess
import os
from datetime import datetime
from app.core.decorators import validate_request

bp = Blueprint('system', __name__, url_prefix='/api/system')

@bp.route('/backup', methods=['POST'])
def create_backup():
    """Genera un backup de la base de datos PostgreSQL."""
    try:
        # Configuración
        db_host = os.getenv('DB_HOST', 'postgres')
        db_user = os.getenv('DB_USER', 'usuario_inventario')
        db_pass = os.getenv('DB_PASSWORD')
        db_name = os.getenv('DB_NAME', 'inventario_db')
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
        backup_filename = f"backup_{timestamp}.dump"
        backup_path = f"/app/backups/{backup_filename}"
        
        # Asegurar que el directorio existe
        os.makedirs('/app/backups', exist_ok=True)
        
        # Comando pg_dump
        # Usamos PGPASSWORD inline para evitar prompt
        env = os.environ.copy()
        env['PGPASSWORD'] = db_pass
        
        command = [
            'pg_dump',
            '-h', db_host,
            '-U', db_user,
            '-d', db_name,
            '-F', 'c',  # Formato custom (comprimido por defecto)
            '-f', backup_path
        ]
        
        result = subprocess.run(
            command, 
            env=env, 
            check=True, 
            capture_output=True, 
            text=True
        )
        
        return jsonify({
            'mensaje': 'Backup creado exitosamente',
            'archivo': backup_filename,
            'ruta': backup_path,
            'timestamp': timestamp
        }), 201
        
    except subprocess.CalledProcessError as e:
        current_app.logger.error(f"Error backup: {e.stderr}")
        return jsonify({
            'error': 'Error al generar backup',
            'detalle': str(e.stderr)
        }), 500
    except Exception as e:
        current_app.logger.error(f"Error general backup: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'detalle': str(e)
        }), 500
@bp.route('/debug/config', methods=['GET'])
def debug_config():
    """Endpoint temporal para depuración."""
    return jsonify({
        'JWT_SECRET_KEY_SET': bool(os.getenv('JWT_SECRET_KEY')),
        'FLASK_ENV': os.getenv('FLASK_ENV'),
        'DB_HOST': os.getenv('DB_HOST'),
        'RESOURCES_LOADED': True
    }), 200
