-- ============================================================
-- Script de preparación de base de datos - CrezcoVe
-- Ejecutar en el servidor PostgreSQL 192.168.100.100
-- como usuario postgres
-- ============================================================

-- 1. Crear base de datos principal de la aplicación
CREATE DATABASE crezco_inventario
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TEMPLATE = template0;

COMMENT ON DATABASE crezco_inventario IS 'Base de datos del sistema de inventario CrezcoVe';

-- 2. Crear base de datos para n8n
CREATE DATABASE crezco_n8n
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TEMPLATE = template0;

COMMENT ON DATABASE crezco_n8n IS 'Base de datos de automatizaciones n8n - CrezcoVe';

-- ============================================================
-- VERIFICACIÓN
-- ============================================================
-- Ejecuta esta consulta para confirmar que las bases de datos
-- fueron creadas correctamente:
-- SELECT datname FROM pg_database WHERE datname LIKE 'crezco%';
