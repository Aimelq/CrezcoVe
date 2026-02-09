import { useLotes } from '@/api/queries/lotes.queries'
import { Calendar, Package, Info, AlertTriangle, ShieldCheck, DollarSign, Box } from 'lucide-react'
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
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {lotes?.map((lote) => (
                        <div key={lote.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
                            <div className="p-5 border-b border-gray-100 bg-gray-50/50">
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="font-bold text-gray-900 line-clamp-1">{lote.producto_nombre}</h3>
                                    <span className="px-2 py-1 bg-primary/10 text-primary text-xs font-bold rounded-md">
                                        Lote: {lote.numero_lote}
                                    </span>
                                </div>
                                <div className="flex items-center gap-2 text-sm text-gray-500">
                                    <Package className="w-4 h-4" />
                                    <span>Stock Actual: <strong>{lote.cantidad_actual}</strong></span>
                                </div>
                            </div>

                            <div className="p-5 space-y-4">
                                <div className="flex justify-between items-center text-sm">
                                    <div className="flex items-center gap-2 text-gray-600">
                                        <Calendar className="w-4 h-4" />
                                        <span>Vencimiento:</span>
                                    </div>
                                    <span className={getPrioridadVencimiento(lote.dias_hasta_vencimiento)}>
                                        {lote.fecha_vencimiento
                                            ? format(new Date(lote.fecha_vencimiento), 'dd MMM yyyy', { locale: es })
                                            : 'S/V (No perecedero)'}
                                    </span>
                                </div>

                                <div className="flex justify-between items-center text-sm">
                                    <div className="flex items-center gap-2 text-gray-600">
                                        <DollarSign className="w-4 h-4" />
                                        <span>Costo Adquisición:</span>
                                    </div>
                                    <span className="font-bold text-gray-900">${lote.costo_lote.toFixed(2)}</span>
                                </div>

                                <div className="pt-4 border-t border-gray-100 flex items-center justify-between">
                                    <div className="flex items-center gap-1 text-xs text-gray-400">
                                        <Info className="w-3 h-3" />
                                        <span>Entrada: {format(new Date(lote.creado_en), 'dd/MM/yy')}</span>
                                    </div>
                                    {lote.dias_hasta_vencimiento !== undefined && (
                                        <div className="flex items-center gap-1">
                                            {lote.dias_hasta_vencimiento <= 7 ? (
                                                <AlertTriangle className="w-4 h-4 text-orange-500" />
                                            ) : (
                                                <ShieldCheck className="w-4 h-4 text-green-500" />
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                    {lotes?.length === 0 && (
                        <div className="col-span-full py-20 bg-white border-2 border-dashed border-gray-200 rounded-2xl flex flex-col items-center justify-center text-gray-400">
                            <Box className="w-16 h-16 mb-4 opacity-20" />
                            <p className="text-lg font-medium">No hay lotes con existencias actualmente</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
