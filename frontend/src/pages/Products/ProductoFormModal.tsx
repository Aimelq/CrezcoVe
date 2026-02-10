import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { X, Loader2, Box, Calendar, Package } from 'lucide-react'
import { useProducto, useCrearProducto, useActualizarProducto, useProductos } from '@/api/queries/productos.queries'
import { useLotesProducto } from '@/api/queries/lotes.queries'
import { format } from 'date-fns'
import SearchableSelect from '@/components/ui/SearchableSelect'
import type { Producto } from '@/types/api.types'

interface ProductoFormModalProps {
    productoId: number | null
    onClose: () => void
}

export default function ProductoFormModal({ productoId, onClose }: ProductoFormModalProps) {
    const { data: producto, isLoading: cargandoProducto } = useProducto(productoId!)
    const { data: todosProductos } = useProductos({ por_pagina: 1000 })
    const crearProducto = useCrearProducto()
    const actualizarProducto = useActualizarProducto()

    const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm<Partial<Producto>>()

    useEffect(() => {
        if (producto) {
            reset(producto)
        }
    }, [producto, reset])

    const onSubmit = (data: Partial<Producto>) => {
        // Limpiar datos para evitar 400 Bad Request por campos numéricos vacíos o inválidos
        const cleanData: any = { ...data };

        // Lista de campos que deben ser numéricos o eliminados si están vacíos/NaN
        const numericFields = [
            'stock_minimo',
            'stock_maximo',
            'precio_venta',
            'margen_deseado',
            'factor_conversion',
            'producto_padre_id'
        ];

        numericFields.forEach(field => {
            const val = cleanData[field];
            if (val === undefined || val === null || val === "" || (typeof val === 'number' && isNaN(val)) || val === "0" || val === 0) {
                // Especial para producto_padre_id: 0 es un valor nulo de facto
                delete cleanData[field];
            } else {
                cleanData[field] = Number(val);
            }
        });

        if (productoId) {
            actualizarProducto.mutate(
                { id: productoId, data: cleanData },
                { onSuccess: onClose }
            )
        } else {
            crearProducto.mutate(cleanData, { onSuccess: onClose })
        }
    }

    const isPending = crearProducto.isPending || actualizarProducto.isPending

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <h2 className="text-2xl font-bold text-gray-900">
                        {productoId ? 'Editar Producto' : 'Nuevo Producto'}
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Formulario */}
                {cargandoProducto && productoId ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                    </div>
                ) : (
                    <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
                        {/* Información básica */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Código SKU *
                                </label>
                                <input
                                    {...register('codigo_sku', { required: 'El SKU es requerido' })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                    placeholder="PROD-001"
                                />
                                {errors.codigo_sku && (
                                    <p className="text-red-500 text-sm mt-1">{errors.codigo_sku.message}</p>
                                )}
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Nombre *
                                </label>
                                <input
                                    {...register('nombre', { required: 'El nombre es requerido' })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                    placeholder="Nombre del producto"
                                />
                                {errors.nombre && (
                                    <p className="text-red-500 text-sm mt-1">{errors.nombre.message}</p>
                                )}
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Descripción
                            </label>
                            <textarea
                                {...register('descripcion')}
                                rows={3}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                placeholder="Descripción del producto"
                            />
                        </div>

                        {/* Stock */}
                        <div className="grid grid-cols-3 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Stock Mínimo *
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    {...register('stock_minimo', { required: true, valueAsNumber: true })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Stock Máximo
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    {...register('stock_maximo', { valueAsNumber: true })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Unidad de Medida
                                </label>
                                <select
                                    {...register('unidad_medida')}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                >
                                    <option value="UNIDAD">Unidad</option>
                                    <option value="CAJA">Caja</option>
                                    <option value="KG">Kilogramo</option>
                                    <option value="LITRO">Litro</option>
                                    <option value="METRO">Metro</option>
                                </select>
                            </div>
                        </div>

                        {/* Fraccionamiento */}
                        <div className="p-4 bg-blue-50/50 rounded-xl border border-blue-100 space-y-4">
                            <h3 className="text-sm font-bold text-blue-900 flex items-center gap-2">
                                <Package className="w-4 h-4" />
                                Fraccionamiento (Multi-unidades)
                            </h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-bold text-blue-700 mb-1 uppercase tracking-wider">
                                        Producto Padre (Bulto/Caja)
                                    </label>
                                    <SearchableSelect
                                        options={todosProductos?.items
                                            .filter(p => p.id !== productoId)
                                            .map(p => ({
                                                id: p.id,
                                                label: p.nombre,
                                                subLabel: `SKU: ${p.codigo_sku} | Stock: ${p.cantidad_actual}`,
                                                value: p.id
                                            })) || []
                                        }
                                        placeholder="Buscar caja/bulto..."
                                        onSelect={(val) => setValue('producto_padre_id', val)}
                                    />
                                    <input type="hidden" {...register('producto_padre_id')} />
                                    <p className="text-[10px] text-blue-600 mt-1 italic">
                                        Selecciona la caja de la cual proviene este producto individual
                                    </p>
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-blue-700 mb-1 uppercase tracking-wider">
                                        Factor de Conversión
                                    </label>
                                    <input
                                        type="number"
                                        step="1"
                                        {...register('factor_conversion', { valueAsNumber: true })}
                                        className="w-full px-3 py-2 bg-white border border-blue-200 rounded-lg focus:ring-2 focus:ring-primary outline-none transition-all text-sm"
                                        placeholder="Ej: 12"
                                    />
                                    <p className="text-[10px] text-blue-600 mt-1 italic">
                                        ¿Cuántos salen de 1 caja?
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Precios */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Precio de Venta *
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    {...register('precio_venta', { required: true, valueAsNumber: true })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                    placeholder="0.00"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Margen Deseado (%)
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    {...register('margen_deseado', { valueAsNumber: true })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                    placeholder="30"
                                />
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            <label className="flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    {...register('tiene_vencimiento')}
                                    className="w-4 h-4 text-primary rounded focus:ring-primary"
                                />
                                <span className="text-sm font-medium text-gray-700">Tiene fecha de vencimiento</span>
                            </label>
                        </div>

                        {/* Desglose por Lotes */}
                        {productoId && (
                            <div className="pt-6 border-t border-gray-200">
                                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <X className="w-5 h-5 text-primary rotate-45" /> {/* Placeholder icon */}
                                    Existencias por Lote
                                </h3>
                                <LotesBreakdown productoId={productoId} />
                            </div>
                        )}

                        {/* Botones */}
                        <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                            >
                                Cancelar
                            </button>
                            <button
                                type="submit"
                                disabled={isPending}
                                className="flex items-center gap-2 bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isPending ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Guardando...
                                    </>
                                ) : (
                                    productoId ? 'Actualizar' : 'Crear Producto'
                                )}
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    )
}

function LotesBreakdown({ productoId }: { productoId: number }) {
    const { data: lotes, isLoading } = useLotesProducto(productoId)

    if (isLoading) {
        return (
            <div className="flex justify-center p-4">
                <Loader2 className="w-6 h-6 animate-spin text-primary" />
            </div>
        )
    }

    if (!lotes || lotes.length === 0) {
        return (
            <div className="text-center p-6 bg-gray-50 rounded-lg border border-dashed border-gray-200">
                <Box className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No hay lotes con existencias para este producto</p>
            </div>
        )
    }

    return (
        <div className="overflow-x-auto rounded-lg border border-gray-200">
            <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                        <th className="px-4 py-2 text-left font-semibold text-gray-700">Lote</th>
                        <th className="px-4 py-2 text-left font-semibold text-gray-700">Stock</th>
                        <th className="px-4 py-2 text-left font-semibold text-gray-700">Costo Unit.</th>
                        <th className="px-4 py-2 text-left font-semibold text-gray-700">Vencimiento</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                    {lotes.map((lote) => (
                        <tr key={lote.id} className="hover:bg-gray-50 transition-colors">
                            <td className="px-4 py-3 font-medium text-gray-900">{lote.numero_lote}</td>
                            <td className="px-4 py-3">
                                <span className="font-bold text-primary">{lote.cantidad_actual}</span>
                            </td>
                            <td className="px-4 py-3 text-gray-600">${lote.costo_lote.toFixed(2)}</td>
                            <td className="px-4 py-3">
                                {lote.fecha_vencimiento ? (
                                    <div className="flex items-center gap-1">
                                        <Calendar className="w-3 h-3 text-gray-400" />
                                        <span className={lote.dias_hasta_vencimiento !== undefined && lote.dias_hasta_vencimiento <= 7 ? 'text-red-600 font-bold' : 'text-gray-600'}>
                                            {format(new Date(lote.fecha_vencimiento), 'dd/MM/yy')}
                                        </span>
                                    </div>
                                ) : (
                                    <span className="text-gray-400">N/A</span>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
