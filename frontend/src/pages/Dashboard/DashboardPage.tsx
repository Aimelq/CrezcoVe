import { useQuery } from '@tanstack/react-query'
import apiClient from '@/api/client'
import type { DashboardData, MovimientosPorDia } from '@/types/api.types'
import {
    DollarSign,
    Package,
    AlertTriangle,
    TrendingDown,
    TrendingUp,
    RefreshCw,
    ArrowUpDown
} from 'lucide-react'
import { useGetTasaCambio } from '@/api/queries/inventario.queries'
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend
} from 'recharts'
import { format, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'

export default function DashboardPage() {
    const { data, isLoading } = useQuery<DashboardData>({
        queryKey: ['dashboardData'],
        queryFn: async () => {
            const response = await apiClient.get('/reportes/dashboard')
            return response.data
        },
    })

    const { data: movimientos7Dias, isLoading: cargandoMovimientos } = useQuery<{ movimientos: MovimientosPorDia[] }>({
        queryKey: ['movimientos-7-dias'],
        queryFn: async () => {
            const response = await apiClient.get('/reportes/movimientos-7-dias')
            return response.data
        },
    })

    const { data: tasaData, isLoading: cargandoTasa } = useGetTasaCambio()

    if (isLoading || cargandoTasa || cargandoMovimientos) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        )
    }

    const chartData = movimientos7Dias?.movimientos.map(m => ({
        ...m,
        fecha_formateada: format(parseISO(m.fecha), 'EEE dd', { locale: es })
    }))

    return (
        <div className="space-y-6">
            {/* Título */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                    <p className="text-gray-600 mt-1">Resumen general en tiempo real</p>
                </div>
                {tasaData && (
                    <div className="bg-white border-2 border-blue-100 rounded-2xl px-6 py-3 flex items-center gap-4 shadow-sm hover:shadow-md transition-shadow">
                        <div className="p-2 bg-blue-50 rounded-xl">
                            <DollarSign className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                            <p className="text-[10px] text-blue-500 font-bold uppercase tracking-widest">Tasa Oficial BCV</p>
                            <p className="text-xl font-black text-blue-900 leading-tight">
                                {tasaData.tasa.toFixed(2)} <span className="text-sm font-medium text-blue-600">Bs/USD</span>
                            </p>
                        </div>
                        <button
                            onClick={() => window.location.reload()} // Simple refresh for now
                            className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Actualizar tasa"
                        >
                            <RefreshCw className="w-4 h-4" />
                        </button>
                    </div>
                )}
            </div>

            {/* Tarjetas de resumen */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Valor Total Inventario */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                            <DollarSign className="w-6 h-6 text-blue-600" />
                        </div>
                    </div>
                    <h3 className="text-sm font-medium text-gray-600 mb-1">
                        Valor Total Inventario
                    </h3>
                    <div className="space-y-1">
                        <p className="text-2xl font-bold text-gray-900">
                            ${data?.valor_total_inventario?.toLocaleString('es-DO', { minimumFractionDigits: 2 }) || '0.00'}
                        </p>
                        {tasaData && (
                            <p className="text-sm font-semibold text-blue-600">
                                ≈ {((data?.valor_total_inventario || 0) * tasaData.tasa).toLocaleString('es-VE', { minimumFractionDigits: 2 })} Bs.
                            </p>
                        )}
                    </div>
                </div>

                {/* Ganancia del Día */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center">
                            <TrendingUp className="w-6 h-6 text-emerald-600" />
                        </div>
                    </div>
                    <h3 className="text-sm font-medium text-gray-600 mb-1">
                        Ganancia Hoy
                    </h3>
                    <div className="space-y-1">
                        <p className="text-2xl font-bold text-gray-900">
                            ${data?.ganancia_hoy?.toLocaleString('es-DO', { minimumFractionDigits: 2 }) || '0.00'}
                        </p>
                        <p className="text-xs text-gray-500">Estimado neto del día</p>
                    </div>
                </div>

                {/* Productos Críticos */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                            <AlertTriangle className="w-6 h-6 text-orange-600" />
                        </div>
                        {data?.productos_criticos && data.productos_criticos > 0 ? (
                            <span className="px-2 py-1 bg-orange-100 text-orange-700 text-[10px] font-bold uppercase rounded-full">
                                Urgente
                            </span>
                        ) : null}
                    </div>
                    <h3 className="text-sm font-medium text-gray-600 mb-1">
                        Productos Críticos
                    </h3>
                    <p className="text-2xl font-bold text-gray-900">
                        {data?.productos_criticos}
                    </p>
                </div>

                {/* Pérdidas del Mes */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                            <TrendingDown className="w-6 h-6 text-red-600" />
                        </div>
                        <span className="text-[10px] font-bold text-red-500 uppercase tracking-wider">Mes actual</span>
                    </div>
                    <h3 className="text-sm font-medium text-gray-600 mb-1">
                        Pérdidas del Mes
                    </h3>
                    <p className="text-2xl font-bold text-gray-900">
                        ${data?.perdidas_mes?.toLocaleString('es-DO', { minimumFractionDigits: 2 }) || '0.00'}
                    </p>
                </div>
            </div>

            {/* Sección de gráficos y alertas */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Gráfico de movimientos */}
                <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                            <ArrowUpDown className="w-5 h-5 text-gray-400" />
                            Actividad de los Últimos 7 Días
                        </h3>
                    </div>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="colorEntradas" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.1} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="colorSalidas" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1} />
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis
                                    dataKey="fecha_formateada"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                                    dy={10}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                                    tickFormatter={(val) => `$${val}`}
                                />
                                <Tooltip
                                    contentStyle={{
                                        borderRadius: '12px',
                                        border: 'none',
                                        boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'
                                    }}
                                />
                                <Legend verticalAlign="top" height={36} align="right" iconType="circle" />
                                <Area
                                    type="monotone"
                                    dataKey="valor_entradas"
                                    name="Compras"
                                    stroke="#10b981"
                                    strokeWidth={3}
                                    fillOpacity={1}
                                    fill="url(#colorEntradas)"
                                />
                                <Area
                                    type="monotone"
                                    dataKey="valor_salidas"
                                    name="Ventas"
                                    stroke="#3b82f6"
                                    strokeWidth={3}
                                    fillOpacity={1}
                                    fill="url(#colorSalidas)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Alertas activas */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-semibold text-gray-900">
                            Panel de Alerta
                        </h3>
                        <span className="px-3 py-1 bg-red-100 text-red-700 text-sm font-bold rounded-lg px-2">
                            {data?.alertas_activas}
                        </span>
                    </div>
                    <div className="space-y-4">
                        {data?.productos_criticos && data.productos_criticos > 0 ? (
                            <div className="p-4 bg-orange-50 border border-orange-100 rounded-xl">
                                <div className="flex items-start gap-3">
                                    <div className="p-2 bg-orange-200 rounded-lg">
                                        <AlertTriangle className="w-5 h-5 text-orange-700 font-black" />
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-bold text-gray-900">
                                            Stock Crítico Detectado
                                        </p>
                                        <p className="text-xs text-orange-800 mt-1 font-medium">
                                            {data?.productos_criticos} productos necesitan reposición inmediata.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-10 text-gray-400">
                                <Package className="w-12 h-12 mb-2 opacity-20" />
                                <p className="text-sm">No hay alertas críticas</p>
                            </div>
                        )}

                        {data?.alertas_activas && data.alertas_activas > 0 ? (
                            <div className="p-4 bg-blue-50 border border-blue-100 rounded-xl">
                                <div className="flex items-start gap-3">
                                    <div className="p-2 bg-blue-200 rounded-lg">
                                        <RefreshCw className="w-4 h-4 text-blue-700 animate-spin-slow" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-bold text-gray-900">Actualización del Sistema</p>
                                        <p className="text-xs text-blue-700 mt-0.5">La tasa BCV y el stock están sincronizados.</p>
                                    </div>
                                </div>
                            </div>
                        ) : null}
                    </div>
                </div>
            </div>
        </div>
    )
}
