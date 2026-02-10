/**
 * Tipos de datos para la API del Sistema de Inventario.
 * Todos los nombres están en español.
 */

export interface Usuario {
    id: number;
    nombre_completo: string;
    email: string;
    telefono?: string;
    rol: 'DUENO' | 'EMPLEADO';
    telegram_chat_id?: string;
    esta_activo: boolean;
    creado_en: string;
    actualizado_en: string;
}

export interface Producto {
    id: number;
    codigo_sku: string;
    nombre: string;
    descripcion?: string;
    categoria_id?: number;
    unidad_medida: string;
    cantidad_actual: number;
    stock_minimo: number;
    stock_maximo?: number;
    umbral_alerta?: number;
    costo_promedio: number;
    ultimo_costo_compra?: number;
    precio_venta: number;
    margen_deseado: number;
    tiene_vencimiento: boolean;
    dias_vencimiento?: number;
    alerta_stock_bajo_notificada: boolean;
    imagen_url?: string;
    notas?: string;
    esta_activo: boolean;
    creado_en: string;
    actualizado_en: string;
    // Fraccionamiento
    producto_padre_id?: number;
    factor_conversion?: number;
    padre?: Producto;
    // Propiedades calculadas
    esta_bajo_stock: boolean;
    margen_actual: number;
    valor_inventario: number;
}

export interface MovimientoInventario {
    id: number;
    producto_id: number;
    usuario_id: number;
    proveedor_id?: number;
    lote_id?: number;
    tipo_movimiento: 'COMPRA' | 'VENTA' | 'AJUSTE' | 'MERMA' | 'TRANSFERENCIA' | 'AUDITORIA';
    cantidad: number;
    cantidad_anterior?: number;
    cantidad_nueva?: number;
    costo_unitario?: number;
    costo_total?: number;
    precio_unitario?: number;
    precio_total?: number;
    motivo_ajuste?: 'DETERIORADO' | 'VENCIDO' | 'USO_INTERNO' | 'ROBO' | 'OTRO';
    referencia_id?: string;
    notas?: string;
    fecha_movimiento: string;
    esta_activo: boolean;
    creado_en: string;
    // Propiedades calculadas
    es_entrada: boolean;
    es_salida: boolean;
    ganancia: number;
}

export interface Proveedor {
    id: number;
    nombre: string;
    nombre_contacto?: string;
    telefono?: string;
    email?: string;
    direccion?: string;
    rif?: string;
    terminos_pago?: string;
    calificacion?: number;
    notas?: string;
    esta_activo: boolean;
    creado_en: string;
    actualizado_en: string;
    cantidad_productos: number;
}

export interface Lote {
    id: number;
    producto_id: number;
    producto_nombre: string;
    numero_lote: string;
    fecha_vencimiento?: string;
    cantidad_inicial: number;
    cantidad_actual: number;
    costo_lote: number;
    proveedor_nombre?: string;
    creado_en: string;
    dias_hasta_vencimiento?: number;
}

export interface Alerta {
    id: number;
    producto_id?: number;
    tipo_alerta: 'STOCK_BAJO' | 'VENCIMIENTO' | 'SIN_MOVIMIENTO' | 'DISCREPANCIA_AUDITORIA' | 'MARGEN_BAJO';
    titulo: string;
    mensaje: string;
    prioridad: 'BAJA' | 'MEDIA' | 'ALTA' | 'CRITICA';
    esta_resuelta: boolean;
    fecha_resolucion?: string;
    resuelta_por_id?: number;
    notas_resolucion?: string;
    notificada: boolean;
    fecha_notificacion?: string;
    datos_adicionales?: any;
    esta_activo: boolean;
    creado_en: string;
}

export interface Categoria {
    id: number;
    nombre: string;
    descripcion?: string;
    icono?: string;
    esta_activo: boolean;
    creado_en: string;
}

// Tipos para requests
export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegistroRequest {
    nombre_completo: string;
    email: string;
    password: string;
    telefono?: string;
    rol?: 'DUENO' | 'EMPLEADO';
}

export interface IngresoInventarioRequest {
    producto_id: number;
    cantidad: number;
    costo_unitario: number;
    proveedor_id?: number;
    referencia_id?: string;
    notas?: string;
    numero_lote?: string;
    fecha_vencimiento?: string;
}

export interface SalidaInventarioRequest {
    producto_id: number;
    cantidad: number;
    precio_unitario: number;
    referencia_id?: string;
    notas?: string;
}

export interface ItemVenta {
    producto_id: number;
    cantidad: number;
    precio_unitario: number;
}

export interface VentaMultipleRequest {
    items: ItemVenta[];
    referencia_id?: string;
    notas?: string;
}

export interface TasaCambio {
    tasa: number;
    ultima_actualización: string;
    moneda_base: string;
    moneda_destino: string;
}

export interface AjusteInventarioRequest {
    producto_id: number;
    cantidad: number;
    motivo_ajuste: 'DETERIORADO' | 'VENCIDO' | 'USO_INTERNO' | 'ROBO' | 'OTRO';
    notas?: string;
}

// Tipos para responses
export interface AuthResponse {
    access_token: string;
    refresh_token: string;
    usuario: Usuario;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    pagina: number;
    paginas_totales: number;
    por_pagina: number;
}

export interface PrediccionAgotamiento {
    tiene_datos: boolean;
    producto_id?: number;
    producto_nombre?: string;
    stock_actual?: number;
    total_vendido_periodo?: number;
    dias_analisis?: number;
    velocidad_venta_diaria?: number;
    dias_hasta_agotar?: number;
    fecha_agotamiento_estimada?: string;
    requiere_pedido?: boolean;
    cantidad_sugerida_pedido?: number;
    nivel_urgencia?: 'SIN_DATOS' | 'AGOTADO' | 'CRITICO' | 'URGENTE' | 'ATENCION' | 'NORMAL';
    mensaje?: string;
}

export interface AnalisisPrecios {
    producto_id: number;
    producto_nombre: string;
    costo_actual: number;
    nuevo_costo: number;
    variacion_costo_porcentaje: number;
    precio_venta_actual: number;
    margen_actual_porcentaje: number;
    margen_con_nuevo_costo_porcentaje: number;
    margen_deseado_porcentaje: number;
    precio_sugerido: number;
    aumento_precio_sugerido: number;
    hay_inflacion: boolean;
    margen_afectado: boolean;
    requiere_atencion: boolean;
    recomendacion: string;
}

export interface DashboardData {
    valor_total_inventario: number;
    total_productos: number;
    productos_criticos: number;
    perdidas_mes: number;
    ganancia_hoy: number;
    alertas_activas: number;
}

export interface MovimientosPorDia {
    fecha: string;
    entradas: number;
    salidas: number;
    valor_entradas: number;
    valor_salidas: number;
}
