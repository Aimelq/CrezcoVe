import { useState } from 'react'
import { useProductos, useEliminarProducto } from '@/api/queries/productos.queries'
import { Package, Plus, Search, Edit, Trash2, AlertTriangle } from 'lucide-react'
import ProductoFormModal from './ProductoFormModal'

export default function ProductosPage() {
    const [buscar, setBuscar] = useState('')
    const [stockBajo, setStockBajo] = useState(false)
    const [modalAbierto, setModalAbierto] = useState(false)
    const [productoEditar, setProductoEditar] = useState<number | null>(null)

    const { data, isLoading } = useProductos({ buscar, stock_bajo: stockBajo })
    const eliminarProducto = useEliminarProducto()

    const handleEliminar = (id: number, nombre: string) => {
        if (confirm(`¿Estás seguro de eliminar el producto "${nombre}"?`)) {
            eliminarProducto.mutate(id)
        }
    }

    const handleNuevo = () => {
        setProductoEditar(null)
        setModalAbierto(true)
    }

    const handleEditar = (id: number) => {
        setProductoEditar(id)
        setModalAbierto(true)
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Productos</h1>
                    <p className="text-gray-600 mt-1">Gestiona tu catálogo de productos</p>
                </div>
                <button
                    onClick={handleNuevo}
                    className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors"
                >
                    <Plus className="w-5 h-5" />
                    Nuevo Producto
                </button>
            </div>

            {/* Filtros */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                <div className="flex gap-4">
                    {/* Búsqueda */}
                    <div className="flex-1 relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                            type="text"
                            value={buscar}
                            onChange={(e) => setBuscar(e.target.value)}
                            placeholder="Buscar por nombre o SKU..."
                            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                        />
                    </div>

                    {/* Filtro stock bajo */}
                    <label className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                        <input
                            type="checkbox"
                            checked={stockBajo}
                            onChange={(e) => setStockBajo(e.target.checked)}
                            className="w-4 h-4 text-primary rounded focus:ring-primary"
                        />
                        <span className="text-sm font-medium text-gray-700">Solo stock bajo</span>
                    </label>
                </div>
            </div>

            {/* Tabla de productos */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                {isLoading ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                    </div>
                ) : data?.items && data.items.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Producto
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        SKU
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Stock
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Precio
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Valor
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Estado
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Acciones
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {data.items.map((producto) => (
                                    <tr key={producto.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                                                    <Package className="w-5 h-5 text-gray-600" />
                                                </div>
                                                <div className="ml-4">
                                                    <div className="text-sm font-medium text-gray-900">{producto.nombre}</div>
                                                    <div className="text-sm text-gray-500">{producto.descripcion}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="text-sm text-gray-900 font-mono">{producto.codigo_sku}</span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-gray-900">
                                                {producto.cantidad_actual} {producto.unidad_medida}
                                            </div>
                                            <div className="text-xs text-gray-500">
                                                Mín: {producto.stock_minimo}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm font-medium text-gray-900">
                                                ${producto.precio_venta.toFixed(2)}
                                            </div>
                                            <div className="text-xs text-gray-500">
                                                Costo: ${producto.costo_promedio.toFixed(2)}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="text-sm font-medium text-gray-900">
                                                ${producto.valor_inventario.toFixed(2)}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {producto.esta_bajo_stock ? (
                                                <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-full">
                                                    <AlertTriangle className="w-3 h-3" />
                                                    Stock Bajo
                                                </span>
                                            ) : (
                                                <span className="inline-flex px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                                                    Normal
                                                </span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <div className="flex items-center justify-end gap-2">
                                                <button
                                                    onClick={() => handleEditar(producto.id)}
                                                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                                    title="Editar"
                                                >
                                                    <Edit className="w-4 h-4" />
                                                </button>
                                                <button
                                                    onClick={() => handleEliminar(producto.id, producto.nombre)}
                                                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                                    title="Eliminar"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center h-64 text-gray-500">
                        <Package className="w-16 h-16 mb-4 text-gray-300" />
                        <p className="text-lg font-medium">No hay productos</p>
                        <p className="text-sm">Comienza agregando tu primer producto</p>
                    </div>
                )}
            </div>

            {/* Paginación */}
            {data && data.paginas_totales > 1 && (
                <div className="flex items-center justify-between bg-white rounded-xl shadow-sm border border-gray-200 px-6 py-4">
                    <div className="text-sm text-gray-700">
                        Mostrando {data.items.length} de {data.total} productos
                    </div>
                    <div className="text-sm text-gray-500">
                        Página {data.pagina} de {data.paginas_totales}
                    </div>
                </div>
            )}

            {/* Modal de formulario */}
            {modalAbierto && (
                <ProductoFormModal
                    productoId={productoEditar}
                    onClose={() => setModalAbierto(false)}
                />
            )}
        </div>
    )
}
