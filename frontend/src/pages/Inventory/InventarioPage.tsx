import { useState, useMemo } from 'react'
import { toast } from 'sonner'
import { useForm } from 'react-hook-form'
import { ArrowDown, ArrowUp, Settings, TrendingUp, Plus, Trash2, ShoppingCart, DollarSign, Info } from 'lucide-react'
import { useProductos } from '@/api/queries/productos.queries'
import { useRegistrarIngreso, useRegistrarVentaMultiple, useRegistrarAjuste, useGetTasaCambio } from '@/api/queries/inventario.queries'
import { useProveedores } from '@/api/queries/proveedores.queries'
import type { IngresoInventarioRequest, SalidaInventarioRequest, AjusteInventarioRequest, ItemVenta, VentaMultipleRequest } from '@/types/api.types'
import SearchableSelect from '@/components/ui/SearchableSelect'

type TipoOperacion = 'ingreso' | 'salida' | 'ajuste'

export default function InventarioPage() {
    const [tipoOperacion, setTipoOperacion] = useState<TipoOperacion>('ingreso')

    // Estado para venta múltiple (Carrito)
    const [carrito, setCarrito] = useState<ItemVenta[]>([])
    const [referenciaVenta, setReferenciaVenta] = useState('')
    const [notasVenta, setNotasVenta] = useState('')

    const { data: productosData } = useProductos({ por_pagina: 1000 })
    const { data: proveedoresData } = useProveedores()
    const { data: tasaData } = useGetTasaCambio()

    const registrarIngreso = useRegistrarIngreso()
    const registrarVentaMultiple = useRegistrarVentaMultiple()
    const registrarAjuste = useRegistrarAjuste()

    const { register: registerIngreso, handleSubmit: handleSubmitIngreso, reset: resetIngreso, setValue: setValueIngreso, watch: watchIngreso } = useForm<IngresoInventarioRequest>()
    const { register: registerSalida, reset: resetSalida, setValue: setValueSalida, watch: watchSalida } = useForm<SalidaInventarioRequest>()
    const { register: registerAjuste, handleSubmit: handleSubmitAjuste, reset: resetAjuste, setValue: setValueAjuste } = useForm<AjusteInventarioRequest>()

    const productoSeleccionadoId = watchIngreso('producto_id')
    const productoSeleccionado = useMemo(() => {
        return productosData?.items.find(p => p.id === productoSeleccionadoId)
    }, [productoSeleccionadoId, productosData])

    const tieneVencimiento = productoSeleccionado?.tiene_vencimiento || false

    // Opciones para selectores con búsqueda
    const opcionesProductos = useMemo(() => {
        if (!productosData || !Array.isArray(productosData.items)) return []
        return productosData.items.map(p => ({
            id: p.id,
            label: p.nombre,
            subLabel: `SKU: ${p.codigo_sku} | Stock: ${p.cantidad_actual}`,
            value: p.id
        }))
    }, [productosData])

    const opcionesProveedores = useMemo(() => {
        if (!proveedoresData || !Array.isArray(proveedoresData.proveedores)) return []
        return proveedoresData.proveedores.map(prov => ({
            id: prov.id,
            label: prov.nombre,
            subLabel: prov.rif || 'Sin RIF',
            value: prov.id
        }))
    }, [proveedoresData])

    const onSubmitIngreso = (data: IngresoInventarioRequest) => {
        registrarIngreso.mutate(data, {
            onSuccess: () => resetIngreso()
        })
    }

    const onSubmitVentaMultiple = () => {
        if (carrito.length === 0) return

        const data: VentaMultipleRequest = {
            items: carrito,
            referencia_id: referenciaVenta || undefined,
            notas: notasVenta || undefined
        }

        registrarVentaMultiple.mutate(data, {
            onSuccess: () => {
                setCarrito([])
                setReferenciaVenta('')
                setNotasVenta('')
            }
        })
    }

    const onSubmitAjuste = (data: AjusteInventarioRequest) => {
        registrarAjuste.mutate(data, {
            onSuccess: () => resetAjuste()
        })
    }

    const agregarAlCarrito = () => {
        const values = watchSalida()
        if (!values.producto_id || !values.cantidad || !values.precio_unitario) return

        const item: ItemVenta = {
            producto_id: Number(values.producto_id),
            cantidad: Number(values.cantidad),
            precio_unitario: Number(values.precio_unitario)
        }
        // Validar stock disponible antes de agregar
        const producto = productosData?.items.find(x => x.id === item.producto_id)
        if (!producto) {
            toast.error('Producto no encontrado')
            return
        }

        // Cantidad ya reservada en el carrito para este producto
        const reservadoEnCarrito = carrito
            .filter(ci => ci.producto_id === item.producto_id)
            .reduce((acc, ci) => acc + Number(ci.cantidad), 0)

        const disponible = Number(producto.cantidad_actual) - reservadoEnCarrito

        if (item.cantidad <= 0) {
            toast.error('La cantidad debe ser mayor que 0')
            return
        }

        if (item.cantidad > disponible) {
            toast.error(`Stock insuficiente. Disponible: ${disponible}`)
            return
        }

        setCarrito([...carrito, item])
        resetSalida({
            producto_id: undefined,
            cantidad: undefined,
            precio_unitario: undefined
        })
    }

    const eliminarDelCarrito = (index: number) => {
        setCarrito(carrito.filter((_, i) => i !== index))
    }

    const totalVentaUsd = carrito.reduce((acc, item) => acc + (item.cantidad * item.precio_unitario), 0)
    const totalVentaBs = tasaData ? totalVentaUsd * tasaData.tasa : 0

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Inventario</h1>
                    <p className="text-gray-600 mt-1">Registra movimientos de entrada, salida y ajustes</p>
                </div>
                {tasaData && (
                    <div className="bg-blue-50 border border-blue-200 rounded-xl px-4 py-3 flex items-center gap-3">
                        <DollarSign className="w-6 h-6 text-blue-600 font-bold" />
                        <div>
                            <p className="text-xs text-blue-600 font-semibold uppercase tracking-wider">Tasa BCV</p>
                            <p className="text-lg font-bold text-blue-900">1 USD = {tasaData.tasa.toFixed(2)} Bs.</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Selector de tipo de operación */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2">
                <div className="grid grid-cols-3 gap-2">
                    <button
                        onClick={() => setTipoOperacion('ingreso')}
                        className={`flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${tipoOperacion === 'ingreso'
                            ? 'bg-green-600 text-white shadow-md'
                            : 'text-gray-600 hover:bg-gray-50'
                            }`}
                    >
                        <ArrowDown className="w-5 h-5" />
                        Ingreso (Compra)
                    </button>
                    <button
                        onClick={() => setTipoOperacion('salida')}
                        className={`flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${tipoOperacion === 'salida'
                            ? 'bg-blue-600 text-white shadow-md'
                            : 'text-gray-600 hover:bg-gray-50'
                            }`}
                    >
                        <ArrowUp className="w-5 h-5" />
                        Salida (Venta)
                    </button>
                    <button
                        onClick={() => setTipoOperacion('ajuste')}
                        className={`flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${tipoOperacion === 'ajuste'
                            ? 'bg-orange-600 text-white shadow-md'
                            : 'text-gray-600 hover:bg-gray-50'
                            }`}
                    >
                        <Settings className="w-5 h-5" />
                        Ajuste
                    </button>
                </div>
            </div>

            {/* Formularios */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Formulario de operación */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
                        {tipoOperacion === 'ingreso' && <><ArrowDown className="text-green-600" /> Registrar Compra</>}
                        {tipoOperacion === 'salida' && <><ArrowUp className="text-blue-600" /> Preparar Venta</>}
                        {tipoOperacion === 'ajuste' && <><Settings className="text-orange-600" /> Registrar Ajuste / Pérdida</>}
                    </h2>

                    {/* Formulario de Ingreso */}
                    {tipoOperacion === 'ingreso' && (
                        <form onSubmit={handleSubmitIngreso(onSubmitIngreso)} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Producto *
                                </label>
                                <SearchableSelect
                                    options={opcionesProductos}
                                    placeholder="Buscar producto por nombre o SKU..."
                                    onSelect={(val) => setValueIngreso('producto_id', val)}
                                />
                                <input type="hidden" {...registerIngreso('producto_id', { required: true })} />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Cantidad *
                                    </label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        {...registerIngreso('cantidad', { required: true, valueAsNumber: true })}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                        placeholder="0"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Costo Unitario ($) *
                                    </label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        {...registerIngreso('costo_unitario', { required: true, valueAsNumber: true })}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                        placeholder="0.00"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Proveedor
                                </label>
                                <SearchableSelect
                                    options={opcionesProveedores}
                                    placeholder="Seleccionar proveedor..."
                                    onSelect={(val) => setValueIngreso('proveedor_id', val)}
                                />
                                <input type="hidden" {...registerIngreso('proveedor_id')} />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Referencia
                                    </label>
                                    <input
                                        {...registerIngreso('referencia_id')}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                        placeholder="FACT-001"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Número de Lote
                                    </label>
                                    <input
                                        {...registerIngreso('numero_lote')}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                        placeholder="LOT-2024-001"
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                {tieneVencimiento ? (
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Fecha de Vencimiento
                                        </label>
                                        <input
                                            type="date"
                                            {...registerIngreso('fecha_vencimiento')}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                        />
                                    </div>
                                ) : (
                                    <div className="flex items-center text-gray-400 text-sm bg-gray-50 rounded-lg p-3">
                                        <Info className="w-4 h-4 mr-2" />
                                        Producto no perecedero
                                    </div>
                                )}
                                <div className="flex items-end">
                                    <button
                                        type="submit"
                                        disabled={registrarIngreso.isPending}
                                        className="w-full bg-green-600 text-white py-2 rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                                    >
                                        <ArrowDown className="w-5 h-5" />
                                        {registrarIngreso.isPending ? 'Registrando...' : 'Registrar'}
                                    </button>
                                </div>
                            </div>
                        </form>
                    )}

                    {/* Formulario de Salida (Preparar Item) */}
                    {tipoOperacion === 'salida' && (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Producto *
                                </label>
                                <SearchableSelect
                                    options={opcionesProductos}
                                    placeholder="Buscar producto por nombre o SKU..."
                                    onSelect={(id) => {
                                        setValueSalida('producto_id', id)
                                        const p = productosData?.items.find(x => x.id === id)
                                        if (p) setValueSalida('precio_unitario', p.precio_venta)
                                    }}
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Cantidad *
                                    </label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        {...registerSalida('cantidad', { required: true, valueAsNumber: true })}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                        placeholder="0"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Precio Unitario ($) *
                                    </label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        {...registerSalida('precio_unitario', { required: true, valueAsNumber: true })}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed outline-none"
                                        placeholder="0.00"
                                        readOnly
                                    />
                                </div>
                            </div>

                            <button
                                type="button"
                                onClick={agregarAlCarrito}
                                className="w-full border-2 border-dashed border-blue-300 text-blue-600 py-3 rounded-xl font-medium hover:bg-blue-50 transition-colors flex items-center justify-center gap-2"
                            >
                                <Plus className="w-5 h-5" />
                                Agregar a la Venta
                            </button>
                        </div>
                    )}

                    {/* Formulario de Ajuste */}
                    {tipoOperacion === 'ajuste' && (
                        <form onSubmit={handleSubmitAjuste(onSubmitAjuste)} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Producto *
                                </label>
                                <SearchableSelect
                                    options={opcionesProductos}
                                    placeholder="Buscar producto..."
                                    onSelect={(val) => setValueAjuste('producto_id', val)}
                                />
                                <input type="hidden" {...registerAjuste('producto_id', { required: true })} />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Cantidad (+ o -) *
                                    </label>
                                    <input
                                        type="number"
                                        {...registerAjuste('cantidad', { required: true, valueAsNumber: true })}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                        placeholder="-10 o +5"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Motivo *
                                    </label>
                                    <select
                                        {...registerAjuste('motivo_ajuste', { required: true })}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                    >
                                        <option value="">Seleccionar</option>
                                        <option value="DETERIORADO">Deteriorado</option>
                                        <option value="VENCIDO">Vencido</option>
                                        <option value="USO_INTERNO">Uso Interno</option>
                                        <option value="ROBO">Robo</option>
                                        <option value="OTRO">Otro</option>
                                    </select>
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={registrarAjuste.isPending}
                                className="w-full bg-orange-600 text-white py-3 rounded-lg font-medium hover:bg-orange-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                            >
                                <Settings className="w-5 h-5" />
                                {registrarAjuste.isPending ? 'Registrando...' : 'Registrar Ajuste'}
                            </button>
                        </form>
                    )}
                </div>

                {/* Carrito de Venta o Info */}
                <div className="space-y-6">
                    {tipoOperacion === 'salida' ? (
                        <div className="bg-white rounded-xl shadow-lg border-2 border-blue-100 flex flex-col h-full overflow-hidden">
                            <div className="p-4 bg-blue-50 border-b border-blue-100 flex items-center justify-between">
                                <h3 className="font-bold text-blue-900 flex items-center gap-2">
                                    <ShoppingCart className="w-5 h-5" />
                                    Detalle de la Venta ({carrito.length})
                                </h3>
                                {carrito.length > 0 && (
                                    <button
                                        onClick={() => setCarrito([])}
                                        className="text-xs text-red-600 font-semibold hover:underline"
                                    >
                                        Limpiar Todo
                                    </button>
                                )}
                            </div>

                            <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-[300px] max-h-[500px]">
                                {carrito.length === 0 ? (
                                    <div className="h-full flex flex-col items-center justify-center text-gray-400 py-10">
                                        <ShoppingCart className="w-12 h-12 mb-2 opacity-20" />
                                        <p>Agrega productos para registrar una venta</p>
                                    </div>
                                ) : (
                                    carrito.map((item, idx) => {
                                        const p = productosData?.items.find(x => x.id === item.producto_id)
                                        return (
                                            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
                                                <div>
                                                    <p className="font-semibold text-gray-900">{p?.nombre}</p>
                                                    <p className="text-xs text-gray-500">
                                                        {item.cantidad} x ${item.precio_unitario.toFixed(2)}
                                                    </p>
                                                </div>
                                                <div className="flex items-center gap-4">
                                                    <p className="font-bold text-gray-900">
                                                        ${(item.cantidad * item.precio_unitario).toFixed(2)}
                                                    </p>
                                                    <button onClick={() => eliminarDelCarrito(idx)} className="text-red-400 hover:text-red-600">
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            </div>
                                        )
                                    })
                                )}
                            </div>

                            {carrito.length > 0 && (
                                <div className="p-4 bg-gray-50 border-t border-gray-200 space-y-4">
                                    <div className="grid grid-cols-2 gap-3">
                                        <input
                                            placeholder="Nro Factura"
                                            value={referenciaVenta}
                                            onChange={(e) => setReferenciaVenta(e.target.value)}
                                            className="px-3 py-2 text-sm border border-gray-300 rounded-lg outline-none"
                                        />
                                        <input
                                            placeholder="Notas..."
                                            value={notasVenta}
                                            onChange={(e) => setNotasVenta(e.target.value)}
                                            className="px-3 py-2 text-sm border border-gray-300 rounded-lg outline-none"
                                        />
                                    </div>

                                    <div className="pt-2 border-t border-gray-200">
                                        <div className="flex justify-between items-center mb-1">
                                            <span className="text-gray-600 font-medium">Total USD:</span>
                                            <span className="text-xl font-black text-gray-900">${totalVentaUsd.toFixed(2)}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-blue-700">
                                            <span className="font-medium">Total Bolívares (Bs.):</span>
                                            <span className="text-2xl font-black">{totalVentaBs.toLocaleString('es-VE', { minimumFractionDigits: 2 })} Bs.</span>
                                        </div>
                                    </div>

                                    <button
                                        onClick={onSubmitVentaMultiple}
                                        disabled={registrarVentaMultiple.isPending}
                                        className="w-full bg-blue-700 text-white py-4 rounded-xl font-bold text-lg hover:bg-blue-800 transition-all shadow-lg flex items-center justify-center gap-2"
                                    >
                                        <TrendingUp className="w-6 h-6" />
                                        {registrarVentaMultiple.isPending ? 'Procesando...' : 'Finalizar Venta'}
                                    </button>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="space-y-6">
                            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl shadow-sm border border-green-200 p-6">
                                <h3 className="text-lg font-semibold text-green-900 mb-3">
                                    💡 Ingreso (Compra)
                                </h3>
                                <ul className="text-sm text-green-800 space-y-2">
                                    <li>• Registra la compra de mercancía de proveedores</li>
                                    <li>• El sistema calcula automáticamente el nuevo costo promedio</li>
                                    <li>• Se analiza si el precio de venta actual sigue siendo rentable</li>
                                </ul>
                            </div>

                            <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl shadow-sm border border-orange-200 p-6">
                                <h3 className="text-lg font-semibold text-orange-900 mb-3">
                                    ⚙️ Ajustes de Inventario
                                </h3>
                                <ul className="text-sm text-orange-800 space-y-2">
                                    <li>• Usa esto para pérdidas, daños o errores de conteo</li>
                                    <li>• Cantidad negativa para pérdidas, positiva para hallazgos</li>
                                    <li>• Es obligatorio especificar un motivo válido</li>
                                </ul>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
