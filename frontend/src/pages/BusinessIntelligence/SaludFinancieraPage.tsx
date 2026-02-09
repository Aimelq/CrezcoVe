import { useQuery } from '@tanstack/react-query'
import {
    TrendingUp,
    AlertCircle,
    DollarSign,
    Clock,
    TrendingDown,
    PieChart as PieChartIcon,
    ArrowRight
} from 'lucide-react'
import {
    PieChart,
    Pie,
    Cell,
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    Legend
} from 'recharts'
import { apiClient } from '@/api/client'
import { cn } from '@/lib/utils'

interface SaludFinancieraData {
    valor_total_inventario: number
    dinero_dormido: number
    porcentaje_dormido: number
    margen_promedio: number
    productos_bajo_margen: number
    ventas_mes_actual: number
    tendencia_ventas_porcentaje: number
    productos_dormidos_top: any[]
}

export default function SaludFinancieraPage() {
    const { data, isLoading, error } = useQuery<SaludFinancieraData>({
        queryKey: ['salud-financiera'],
        queryFn: async () => {
            const { data } = await apiClient.get('/inteligencia/salud-financiera')
            return data
        }
    })

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        )
    }

    if (error || !data) {
        return (
            <div className="p-6 text-center text-red-600 bg-red-50 rounded-xl border border-red-100">
                <AlertCircle className="w-12 h-12 mx-auto mb-4" />
                <h3 className="text-lg font-bold">Error al cargar datos</h3>
                <p>No pudimos obtener la información de salud financiera. Por favor intente más tarde.</p>
            </div>
        )
    }

    const pieData = [
        { name: 'Capital Activo', value: data.valor_total_inventario - data.dinero_dormido },
        { name: 'Dinero Dormido', value: data.dinero_dormido }
    ]

    const COLORS = ['#2563eb', '#f87171']

    return (
        <div className="p-6 space-y-8 animate-in fade-in duration-500">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Salud Financiera</h1>
                <p className="text-gray-500 mt-1 uppercase text-xs font-bold tracking-widest">
                    Análisis de Capital e Inteligencia de Inventario
                </p>
            </div>

            {/* KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Valor de Inventario"
                    value={`$${data.valor_total_inventario.toLocaleString()}`}
                    icon={DollarSign}
                    description="Capital total en mercancía"
                    color="text-blue-600"
                    bg="bg-blue-50"
                />
                <StatCard
                    title="Dinero Dormido"
                    value={`$${data.dinero_dormido.toLocaleString()}`}
                    icon={Clock}
                    description="Sin ventas por 60+ días"
                    color="text-red-600"
                    bg="bg-red-50"
                />
                <StatCard
                    title="Margen Promedio"
                    value={`${data.margen_promedio}%`}
                    icon={TrendingUp}
                    description="Rendimiento del catálogo"
                    color="text-emerald-600"
                    bg="bg-emerald-50"
                />
                <StatCard
                    title="Ventas del Mes"
                    value={`$${data.ventas_mes_actual.toLocaleString()}`}
                    icon={data.tendencia_ventas_porcentaje >= 0 ? TrendingUp : TrendingDown}
                    description={`${data.tendencia_ventas_porcentaje}% vs mes anterior`}
                    color={data.tendencia_ventas_porcentaje >= 0 ? "text-emerald-600" : "text-red-600"}
                    bg={data.tendencia_ventas_porcentaje >= 0 ? "bg-emerald-50" : "bg-red-50"}
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Gráfico de Distribución de Capital */}
                <div className="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
                            <PieChartIcon className="w-5 h-5" />
                        </div>
                        <h2 className="text-xl font-bold text-gray-900">Distribución de Capital</h2>
                    </div>
                    <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={80}
                                    outerRadius={100}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {pieData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    formatter={(value: number) => `$${value.toLocaleString()}`}
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                                />
                                <Legend verticalAlign="bottom" height={36} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="mt-6 p-4 bg-gray-50 rounded-xl border border-gray-100">
                        <p className="text-sm text-gray-600 leading-relaxed text-center">
                            Actualmente tienes el <span className="font-bold text-red-600">{data.porcentaje_dormido}%</span> de tu inversión inmovilizada en productos sin rotación.
                        </p>
                    </div>
                </div>

                {/* Top Dinero Dormido - Accionable */}
                <div className="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="p-2 bg-red-100 rounded-lg text-red-600">
                            <AlertCircle className="w-5 h-5" />
                        </div>
                        <h2 className="text-xl font-bold text-gray-900">Alertas de Liquidación</h2>
                    </div>

                    <div className="space-y-4">
                        {data.productos_dormidos_top.map((item) => (
                            <div key={item.producto_id} className="group p-4 rounded-xl border border-gray-100 hover:border-red-200 hover:bg-red-50/30 transition-all duration-300">
                                <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                        <h3 className="font-bold text-gray-900 group-hover:text-red-700 transition-colors uppercase text-sm">{item.nombre}</h3>
                                        <p className="text-xs text-gray-500 mt-1">Capital frozen: <span className="font-bold text-gray-700">${item.valor_inmovilizado}</span></p>
                                        <p className="text-xs text-gray-400 font-medium">Lleva {item.dias_sin_venta} días sin venderse</p>
                                    </div>
                                    <div className="text-right">
                                        <div className="inline-flex flex-col items-end">
                                            <span className="text-[10px] font-bold text-red-600 uppercase tracking-tighter mb-1">Oferta Sugerida</span>
                                            <div className="flex items-center gap-2">
                                                <span className="text-xs line-through text-gray-400">${item.precio_venta}</span>
                                                <span className="text-lg font-black text-emerald-600">${item.precio_con_descuento}</span>
                                            </div>
                                            <span className="bg-emerald-100 text-emerald-700 text-[10px] px-2 py-0.5 rounded-full font-bold mt-1">
                                                -{item.descuento_sugerido_porcentaje}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <button className="w-full mt-4 py-2 bg-white border border-gray-200 rounded-lg text-xs font-bold text-gray-600 hover:bg-primary hover:text-white hover:border-primary transition-all flex items-center justify-center gap-2 group-hover:shadow-md">
                                    Aplicar Promoción <ArrowRight className="w-3 h-3" />
                                </button>
                            </div>
                        ))}

                        {data.productos_dormidos_top.length === 0 && (
                            <div className="text-center py-12">
                                <p className="text-gray-400 font-medium">No se detectó dinero dormido significativo. ¡Tu inventario tiene buena rotación!</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

function StatCard({ title, value, icon: Icon, description, color, bg }: any) {
    return (
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4">
                <div className={cn("p-3 rounded-xl", bg, color)}>
                    <Icon className="w-6 h-6" />
                </div>
                <div>
                    <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">{title}</h3>
                    <p className={cn("text-2xl font-black mt-1", color)}>{value}</p>
                    <p className="text-xs text-gray-500 font-medium mt-1">{description}</p>
                </div>
            </div>
        </div>
    )
}
