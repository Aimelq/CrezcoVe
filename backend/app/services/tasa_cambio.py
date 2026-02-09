"""
Servicio de Tasa de Cambio BCV.
Obtiene la tasa oficial del Banco Central de Venezuela.
"""
import requests
import logging
from datetime import datetime
from app.core.extensions import db
from app.models.configuracion import Configuracion

logger = logging.getLogger(__name__)

class TasaCambioServicio:
    """Servicio para gestionar la tasa de cambio del dólar."""
    
    CLAVE_TASA = 'tasa_dolar_bcv'
    CLAVE_FECHA = 'ultima_actualizacion_tasa'
    
    @staticmethod
    def _intentar_bcv_oficial():
        """Intenta obtener la tasa directamente del sitio web del BCV."""
        try:
            import re
            logger.info("Consultando sitio oficial bcv.org.ve...")
            # BCV a veces tiene problemas de certificados, usamos verify=False
            response = requests.get('https://www.bcv.org.ve/', timeout=10, verify=False)
            if response.status_code == 200:
                html = response.text
                # Buscar el bloque del dólar
                # Estructura: <div id="dolar" ...> ... <strong> 36,1234 </strong>
                match = re.search(r'id="dolar".*?<strong>\s*([\d,\.]+)\s*</strong>', html, re.DOTALL)
                if match:
                    tasa_str = match.group(1).replace(',', '.')
                    return float(tasa_str)
            return None
        except Exception as e:
            logger.error(f"Error al scrapear sitio oficial BCV: {e}")
            return None

    @staticmethod
    def obtener_tasa_bcv(forzar=False):
        """
        Obtiene la tasa oficial. Prioriza el sitio oficial del BCV.
        Mecanismo de caché: solo consulta externamente una vez por hora (si no es forzado).
        """
        ultima_fecha_str = Configuracion.get_valor(TasaCambioServicio.CLAVE_FECHA)
        if not forzar and ultima_fecha_str:
            try:
                ultima_fecha = datetime.fromisoformat(ultima_fecha_str)
                diferencia = datetime.now() - ultima_fecha
                if diferencia.total_seconds() < 3600:  # 1 hora
                    tasa_db = Configuracion.get_valor(TasaCambioServicio.CLAVE_TASA)
                    if tasa_db:
                        return float(tasa_db)
            except Exception:
                pass

        # 1. Intentar Scraper Oficial (El más confiable para el valor exacto)
        tasa = TasaCambioServicio._intentar_bcv_oficial()
        if tasa:
            logger.info(f"Tasa obtenida de BCV Oficial: {tasa}")
            TasaCambioServicio.actualizar_tasa(tasa)
            return tasa

        try:
            # 2. Intentar con Open Exchange Rates API (Fallback 1)
            logger.info("Consultando tasa a través de API alternativa (ExchangeRate API)...")
            response = requests.get('https://open.er-api.com/v6/latest/USD', timeout=7)
            if response.status_code == 200:
                data = response.json()
                tasa = data.get('rates', {}).get('VES')
                
                if tasa:
                    logger.info(f"Tasa BCV obtenida de ExchangeRate: {tasa}")
                    TasaCambioServicio.actualizar_tasa(tasa)
                    return float(tasa)
            
            # 3. Otros fallbacks conocidos (pueden estar caídos)
            api_fallbacks = [
                'https://ve.dolarapi.com/v1/dolares/bcv',
                'https://pydolarvenezuela-api.vercel.app/api/v1/dollar?page=bcv'
            ]
            
            for url in api_fallbacks:
                try:
                    logger.info(f"Intentando fallback: {url}")
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        # Lógica simplificada de extracción según el proveedor
                        tasa_val = (data.get('promedio') or 
                                   data.get('monitors', {}).get('usd', {}).get('price'))
                        if tasa_val:
                            TasaCambioServicio.actualizar_tasa(tasa_val)
                            return float(tasa_val)
                except Exception:
                    continue

            logger.warning("No se pudo obtener la tasa de ninguna fuente externa.")
        except Exception as e:
            logger.error(f"Error excepcional al obtener tasa BCV: {e}")
        
        # Fallback Final: Base de datos
        tasa_str = Configuracion.get_valor(TasaCambioServicio.CLAVE_TASA)
        if tasa_str:
            logger.info(f"Usando última tasa guardada en BD: {tasa_str}")
            return float(tasa_str)
        
        return 0.0

    @staticmethod
    def actualizar_tasa(tasa):
        """Actualiza la tasa en la configuración del sistema."""
        Configuracion.set_valor(
            TasaCambioServicio.CLAVE_TASA, 
            str(tasa), 
            "Tasa oficial del BCV (Bs. por USD)",
            "FINANZAS"
        )
        Configuracion.set_valor(
            TasaCambioServicio.CLAVE_FECHA, 
            datetime.now().isoformat(),
            "Última vez que se actualizó la tasa",
            "FINANZAS"
        )
        return True

    @staticmethod
    def convertir_a_bs(monto_usd):
        """Convierte un monto en USD a Bolívares."""
        tasa = TasaCambioServicio.obtener_tasa_bcv()
        return round(float(monto_usd) * tasa, 2)

    @staticmethod
    def get_info_tasa():
        """Retorna información completa sobre la tasa actual."""
        return {
            'tasa': float(Configuracion.get_valor(TasaCambioServicio.CLAVE_TASA, 0.0)),
            'ultima_actualización': Configuracion.get_valor(TasaCambioServicio.CLAVE_FECHA),
            'moneda_base': 'USD',
            'moneda_destino': 'VES'
        }
