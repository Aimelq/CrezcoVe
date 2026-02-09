from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError

def validate_request(schema_class):
    """
    Decorador para validar el body de la petición contra un esquema de Marshmallow.
    
    Args:
        schema_class: Clase del esquema de Marshmallow a usar para validación
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            schema = schema_class()
            try:
                # Validar el JSON recibido
                json_data = request.get_json()
                if not json_data:
                    return jsonify({"error": "No se enviaron datos JSON"}), 400
                
                # Si la validación es exitosa, continuamos
                schema.load(json_data)
                
            except ValidationError as err:
                # Si hay error de validación, retornamos 400 con los detalles
                return {
                    "error": "Error de validación",
                    "mensaje": "Los datos enviados son inválidos",
                    "detalles": err.messages
                }, 400
            except Exception as e:
                return {"error": "Error procesando la solicitud", "mensaje": str(e)}, 400
                
            return f(*args, **kwargs)
        return wrapper
    return decorator
