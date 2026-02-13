import { useState } from 'react'
import apiClient from '@/api/client'
import { FileSpreadsheet, Download, Calendar, Loader2, Check } from 'lucide-react'
import { toast } from 'sonner'
import { format } from 'date-fns'

export default function ReporteVentasPage() {
    const [tipoReporte, setTipoReporte] = useState<'mensual' | 'diario'>('mensual')

    // Mes/Año para reporte mensual
    const [mes, setMes] = useState<string>(new Date().getMonth().toString())
    const [anio, setAnio] = useState<string>(new Date().getFullYear().toString())

    // Fecha para reporte diario (YYYY-MM-DD)
    const [fechaDiaria, setFechaDiaria] = useState<string>(format(new Date(), 'yyyy-MM-dd'))

    const [isDownloading, setIsDownloading] = useState(false)

    const meses = [
        { value: '0', label: 'Enero' },
        { value: '1', label: 'Febrero' },
        { value: '2', label: 'Marzo' },
        { value: '3', label: 'Abril' },
        { value: '4', label: 'Mayo' },
        { value: '5', label: 'Junio' },
        { value: '6', label: 'Julio' },
        { value: '7', label: 'Agosto' },
        { value: '8', label: 'Septiembre' },
        { value: '9', label: 'Octubre' },
        { value: '10', label: 'Noviembre' },
        { value: '11', label: 'Diciembre' },
    ]

    const anios = Array.from({ length: 5 }, (_, i) => (new Date().getFullYear() - i).toString())

    const handleDownload = async () => {
        try {
            setIsDownloading(true)

            const params: any = { tipo: tipoReporte }
            let filename = ''

            if (tipoReporte === 'mensual') {
                const mesReal = parseInt(mes) + 1
                params.mes = mesReal
                params.anio = parseInt(anio)
                filename = `Ventas_Mensual_${mesReal.toString().padStart(2, '0')}_${anio}.xlsx`
            } else {
                params.fecha = fechaDiaria
                filename = `Ventas_Diario_${fechaDiaria}.xlsx`
            }

            const response = await apiClient.get('/reportes/ventas/excel', {
                params,
                responseType: 'blob'
            })

            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', filename)
            document.body.appendChild(link)
            link.click()
            link.remove()
            window.URL.revokeObjectURL(url)

            toast.success('Reporte descargado exitosamente')
        } catch (error) {
            console.error('Error al descargar reporte:', error)
            toast.error('Error al generar el reporte. Intente nuevamente.')
        } finally {
            setIsDownloading(false)
        }
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Reporte de Ventas</h1>
                <p className="text-gray-600 mt-1">Genera reportes detallados o agrupados para tu control.</p>
            </div>

            <div className="max-w-xl bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-6 border-b border-gray-200">
                    <div className="flex items-center gap-2">
                        <FileSpreadsheet className="w-5 h-5 text-green-600" />
                        <div>
                            <h2 className="text-lg font-semibold text-gray-900">Exportar a Excel</h2>
                            <p className="text-sm text-gray-500">Selecciona el tipo de reporte y los parámetros.</p>
                        </div>
                    </div>
                </div>

                <div className="p-6 space-y-6">
                    {/* Selector de Tipo */}
                    <div className="grid grid-cols-2 gap-4 p-1 bg-gray-100 rounded-lg">
                        <button
                            onClick={() => setTipoReporte('mensual')}
                            className={`flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-all ${tipoReporte === 'mensual'
                                    ? 'bg-white text-gray-900 shadow-sm'
                                    : 'text-gray-500 hover:text-gray-900'
                                }`}
                        >
                            <Calendar className="w-4 h-4" />
                            Mensual (Por Día)
                        </button>
                        <button
                            onClick={() => setTipoReporte('diario')}
                            className={`flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-all ${tipoReporte === 'diario'
                                    ? 'bg-white text-gray-900 shadow-sm'
                                    : 'text-gray-500 hover:text-gray-900'
                                }`}
                        >
                            <Check className="w-4 h-4" />
                            Diario (Detallado)
                        </button>
                    </div>

                    {/* Controles dinámicos */}
                    {tipoReporte === 'mensual' ? (
                        <div className="grid grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-2 duration-200">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700">Mes</label>
                                <select
                                    value={mes}
                                    onChange={(e) => setMes(e.target.value)}
                                    className="w-full flex h-10 w-full items-center justify-between rounded-md border border-gray-200 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                >
                                    {meses.map((m) => (
                                        <option key={m.value} value={m.value}>{m.label}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700">Año</label>
                                <select
                                    value={anio}
                                    onChange={(e) => setAnio(e.target.value)}
                                    className="w-full flex h-10 w-full items-center justify-between rounded-md border border-gray-200 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                >
                                    {anios.map((a) => (
                                        <option key={a} value={a}>{a}</option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-2 animate-in fade-in slide-in-from-top-2 duration-200">
                            <label className="text-sm font-medium text-gray-700">Fecha del Reporte</label>
                            <input
                                type="date"
                                value={fechaDiaria}
                                onChange={(e) => setFechaDiaria(e.target.value)}
                                className="w-full flex h-10 w-full items-center justify-between rounded-md border border-gray-200 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            />
                        </div>
                    )}

                    {/* Información del contenido */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
                        <Calendar className="w-5 h-5 text-blue-600 mt-0.5" />
                        <div className="text-sm text-blue-800">
                            <p className="font-medium">
                                {tipoReporte === 'mensual' ? 'Reporte Mensual Agrupado:' : 'Reporte Diario Detallado:'}
                            </p>
                            <ul className="list-disc list-inside mt-1 space-y-1 text-blue-700">
                                {tipoReporte === 'mensual' ? (
                                    <>
                                        <li>Resumen día por día</li>
                                        <li>Total vendido por día</li>
                                        <li>Cantidad de ventas por día</li>
                                        <li>Sin detalle de productos</li>
                                    </>
                                ) : (
                                    <>
                                        <li>Lista de todas las ventas del día</li>
                                        <li>Hora exacta y referencia</li>
                                        <li>Monto total por venta</li>
                                        <li>Sin detalle de productos</li>
                                    </>
                                )}
                            </ul>
                        </div>
                    </div>

                    <button
                        onClick={handleDownload}
                        disabled={isDownloading}
                        className="w-full inline-flex items-center justify-center rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none transition-colors"
                    >
                        {isDownloading ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Generando archivo...
                            </>
                        ) : (
                            <>
                                <Download className="mr-2 h-4 w-4" />
                                Descargar Reporte Excel
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    )
}
