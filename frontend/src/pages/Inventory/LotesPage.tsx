import { useLotes } from '@/api/queries/lotes.queries'
import { Calendar, Package, AlertTriangle, ShieldCheck, DollarSign, Box } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

export default function LotesPage() {
    const { data: lotes, isLoading } = useLotes()

    const getPrioridadVencimiento = (dias?: number) => {
        if (dias === undefined) return 'text-gray-400'
        if (dias <= 0) return 'text-red-600 font-bold'
        if (dias <= 7) return 'text-orange-500 font-bold'
        if (dias <= 30) return 'text-yellow-600'
        return 'text-green-600'
    }

    const getEstadoVencimiento = (dias?: number) => {
        if (dias === undefined) return { texto: 'No Perecedero', color: 'bg-gray-100 text-gray-600' }
        if (dias <= 0) return { texto: 'Vencido', color: 'bg-red-100 text-red-700' }
        if (dias <= 7) return { texto: 'Por Vencer', color: 'bg-orange-100 text-orange-700' }
        if (dias <= 30) return { texto: 'Próximo', color: 'bg-yellow-100 text-yellow-700' }
        return { texto: 'Normal', color: 'bg-green-100 text-green-700' }
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Gestión de Lotes</h1>
                    <p className="text-gray-600 mt-1">Visualiza el desglose de tu inventario por fecha de entrada y vencimiento</p>
                </div>
            </div>

            {isLoading ? (
                <div className="flex justify-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                </div>
            ) : lotes && lotes.length > 0 ? (
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Producto
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Lote
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Vencimiento
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Stock
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Inicial
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Costo
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Estado
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {lotes.map((lote) => {
                                    const estado = getEstadoVencimiento(lote.dias_hasta_vencimiento)
                                    return (
                                        <tr key={lote.id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4">
                                                <div className="flex items-center">
                                                    <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center mr-3">
                                                        <Package className="w-5 h-5 text-primary" />
                                                    </div>
                                                    <div>
                                                        <div className="text-sm font-medium text-gray-900">{lote.producto_nombre}</div>
                                                        <div className="text-xs text-gray-500">Entrada: {format(new Date(lote.creado_en), 'dd/MM/yy', { locale: es })}</div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="text-sm font-mono font-bold text-primary">{lote.numero_lote}</span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-2">
                                                    <Calendar className="w-4 h-4 text-gray-400" />
                                                    <span className={`text-sm ${getPrioridadVencimiento(lote.dias_hasta_vencimiento)}`}>
                                                        {lote.fecha_vencimiento
                                                            ? format(new Date(lote.fecha_vencimiento), 'dd MMM yyyy', { locale: es })
                                                            : 'S/V'}
                                                    </span>
                                                </div>
                                                {lote.dias_hasta_vencimiento !== undefined && (
                                                    <div className="text-xs text-gray-500 mt-1">
                                                        {lote.dias_hasta_vencimiento > 0 ? `${lote.dias_hasta_vencimiento} días` : 'Vencido'}
                                                    </div>
                                                )}
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="text-sm font-bold text-gray-900">{lote.cantidad_actual}</span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="text-sm text-gray-600">{lote.cantidad_inicial}</span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-1">
                                                    <DollarSign className="w-4 h-4 text-green-600" />
                                                    <span className="text-sm font-semibold text-gray-900">{lote.costo_lote.toFixed(2)}</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-2">
                                                    <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${estado.color}`}>
                                                        {lote.dias_hasta_vencimiento !== undefined && lote.dias_hasta_vencimiento <= 7 ? (
                                                            <AlertTriangle className="w-3 h-3" />
                                                        ) : lote.dias_hasta_vencimiento !== undefined ? (
                                                            <ShieldCheck className="w-3 h-3" />
                                                        ) : null}
                                                        {estado.texto}
                                                    </span>
                                                </div>
                                            </td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            ) : (
                <div className="col-span-full py-20 bg-white border-2 border-dashed border-gray-200 rounded-2xl flex flex-col items-center justify-center text-gray-400">
                    <Box className="w-16 h-16 mb-4 opacity-20" />
                    <p className="text-lg font-medium">No hay lotes con existencias actualmente</p>
                </div>
            )}
        </div>
    )
}
