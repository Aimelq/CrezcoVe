import { useQuery } from '@tanstack/react-query'
import apiClient from '@/api/client'
import { FileText, TrendingDown, AlertTriangle, Package } from 'lucide-react'

export default function ReportesPage() {
    const { data: dineroDormido } = useQuery({
        queryKey: ['dinero-dormido'],
        queryFn: async () => {
            const response = await apiClient.get('/inventario/reporte-dinero-dormido', {
                params: { dias: 60 }
            })
            return response.data
        },
    })

    const { data: productosCriticos } = useQuery({
        queryKey: ['productos-criticos'],
        queryFn: async () => {
            const response = await apiClient.get('/reportes/productos-criticos', {
                params: { limite: 10 }
            })
            return response.data
        },
    })

    const { data: alertas } = useQuery({
        queryKey: ['alertas-activas'],
        queryFn: async () => {
            const response = await apiClient.get('/reportes/alertas-activas')
            return response.data
        },
    })

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Reportes</h1>
                <p className="text-gray-600 mt-1">Análisis inteligente de tu inventario</p>
            </div>

            {/* Resumen de reportes */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl shadow-sm border border-orange-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 bg-orange-500 rounded-lg flex items-center justify-center">
                            <TrendingDown className="w-6 h-6 text-white" />
                        </div>
                    </div>
                    <h3 className="text-sm font-medium text-orange-900 mb-1">
                        Dinero Dormido
                    </h3>
                    <p className="text-2xl font-bold text-orange-900">
                        ${dineroDormido?.valor_total_inmovilizado?.toLocaleString('es-DO', { minimumFractionDigits: 2 }) || '0.00'}
                    </p>
                    <p className="text-xs text-orange-700 mt-2">
                        {dineroDormido?.total_productos_sin_movimiento || 0} productos sin movimiento
                    </p>
                </div>

                <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl shadow-sm border border-red-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 bg-red-500 rounded-lg flex items-center justify-center">
                            <AlertTriangle className="w-6 h-6 text-white" />
                        </div>
                    </div>
                    <h3 className="text-sm font-medium text-red-900 mb-1">
                        Productos Críticos
                    </h3>
                    <p className="text-2xl font-bold text-red-900">
                        {productosCriticos?.total || 0}
                    </p>
                    <p className="text-xs text-red-700 mt-2">
                        Requieren atención urgente
                    </p>
                </div>

                <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-xl shadow-sm border border-yellow-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 bg-yellow-500 rounded-lg flex items-center justify-center">
                            <FileText className="w-6 h-6 text-white" />
                        </div>
                    </div>
                    <h3 className="text-sm font-medium text-yellow-900 mb-1">
                        Alertas Activas
                    </h3>
                    <p className="text-2xl font-bold text-yellow-900">
                        {alertas?.total || 0}
                    </p>
                    <p className="text-xs text-yellow-700 mt-2">
                        Pendientes de resolución
                    </p>
                </div>
            </div>

            {/* Dinero Dormido */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-6 border-b border-gray-200">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                            <TrendingDown className="w-5 h-5 text-orange-600" />
                        </div>
                        <div>
                            <h2 className="text-xl font-semibold text-gray-900">
                                💤 Dinero Dormido
                            </h2>
                            <p className="text-sm text-gray-600">
                                Productos sin movimiento en los últimos 60 días
                            </p>
                        </div>
                    </div>
                </div>

                <div className="p-6">
                    {dineroDormido?.productos && dineroDormido.productos.length > 0 ? (
                        <div className="space-y-4">
                            {dineroDormido.productos.map((item: any) => (
                                <div
                                    key={item.producto_id}
                                    className="p-4 bg-orange-50 border border-orange-200 rounded-lg"
                                >
                                    <div className="flex items-start justify-between mb-2">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                                                <Package className="w-5 h-5 text-orange-600" />
                                            </div>
                                            <div>
                                                <h3 className="font-medium text-gray-900">{item.nombre}</h3>
                                                <p className="text-sm text-gray-600">
                                                    {item.dias_sin_venta} días sin venta
                                                </p>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-lg font-bold text-orange-900">
                                                ${item.valor_inmovilizado.toLocaleString('es-DO', { minimumFractionDigits: 2 })}
                                            </p>
                                            <p className="text-xs text-orange-700">
                                                Stock: {item.stock_actual}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="mt-3 p-3 bg-white rounded-lg">
                                        <p className="text-sm text-gray-700">
                                            <strong className="text-orange-700">Sugerencia:</strong>{' '}
                                            Descuento del {item.descuento_sugerido_porcentaje}% para liquidar
                                        </p>
                                        <p className="text-xs text-gray-600 mt-1">
                                            {item.recomendacion}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-gray-500">
                            <TrendingDown className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                            <p>No hay productos sin movimiento</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Productos Críticos */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-6 border-b border-gray-200">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                            <AlertTriangle className="w-5 h-5 text-red-600" />
                        </div>
                        <div>
                            <h2 className="text-xl font-semibold text-gray-900">
                                ⚠️ Productos Críticos
                            </h2>
                            <p className="text-sm text-gray-600">
                                Productos que requieren reposición urgente
                            </p>
                        </div>
                    </div>
                </div>

                <div className="p-6">
                    {productosCriticos?.productos_criticos && productosCriticos.productos_criticos.length > 0 ? (
                        <div className="space-y-4">
                            {productosCriticos.productos_criticos.map((item: any) => (
                                <div
                                    key={item.producto_id}
                                    className="p-4 bg-red-50 border border-red-200 rounded-lg"
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                                                <Package className="w-5 h-5 text-red-600" />
                                            </div>
                                            <div>
                                                <h3 className="font-medium text-gray-900">{item.producto_nombre}</h3>
                                                <p className="text-sm text-gray-600">
                                                    Stock actual: {item.stock_actual} | Mínimo: {item.stock_minimo}
                                                </p>
                                                {item.dias_hasta_agotar && (
                                                    <p className="text-xs text-red-700 mt-1">
                                                        ⏰ Se agotará en {Math.ceil(item.dias_hasta_agotar)} días
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${item.nivel_urgencia === 'CRITICO' ? 'bg-red-600 text-white' :
                                                item.nivel_urgencia === 'URGENTE' ? 'bg-orange-600 text-white' :
                                                    'bg-yellow-600 text-white'
                                                }`}>
                                                {item.nivel_urgencia}
                                            </span>
                                        </div>
                                    </div>
                                    {item.cantidad_sugerida_pedido && (
                                        <div className="mt-3 p-3 bg-white rounded-lg">
                                            <p className="text-sm text-gray-700">
                                                <strong className="text-red-700">Sugerencia de pedido:</strong>{' '}
                                                {item.cantidad_sugerida_pedido} unidades
                                            </p>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-gray-500">
                            <AlertTriangle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                            <p>No hay productos críticos</p>
                        </div>
                    )}
                </div>
            </div>

        </div>
    )
}
