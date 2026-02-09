"""
Endpoints de Inteligencia de Negocio.
Provee métricas avanzadas y salud financiera.
"""
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from app.services.inteligencia_negocio import ServicioInteligenciaNegocio

# Crear namespace
inteligencia_ns = Namespace('inteligencia', description='Métricas avanzadas e inteligencia de negocio')

@inteligencia_ns.route('/salud-financiera')
class SaludFinanciera(Resource):
    @jwt_required()
    def get(self):
        """Obtiene métricas detalladas de la salud financiera del negocio."""
        return ServicioInteligenciaNegocio.obtener_resumen_salud_financiera()

@inteligencia_ns.route('/insights-semanales')
class InsightsSemanales(Resource):
    @jwt_required()
    def get(self):
        """Obtiene el reporte narrativo de AI Insights (útil para previsualización)."""
        return ServicioInteligenciaNegocio.generar_insights_semanales()
