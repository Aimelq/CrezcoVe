import { useState } from 'react'
import { useProveedores } from '@/api/queries/proveedores.queries'
import { Users, Plus, Phone, Mail, MapPin, Edit } from 'lucide-react'
import ProveedorFormModal from './ProveedorFormModal'

export default function ProveedoresPage() {
    const [modalAbierto, setModalAbierto] = useState(false)
    const [proveedorEditar, setProveedorEditar] = useState<number | null>(null)

    const { data, isLoading } = useProveedores()

    const handleNuevo = () => {
        setProveedorEditar(null)
        setModalAbierto(true)
    }

    const handleEditar = (id: number) => {
        setProveedorEditar(id)
        setModalAbierto(true)
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Proveedores</h1>
                    <p className="text-gray-600 mt-1">Administra tus proveedores y genera pedidos inteligentes</p>
                </div>
                <button
                    onClick={handleNuevo}
                    className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors"
                >
                    <Plus className="w-5 h-5" />
                    Nuevo Proveedor
                </button>
            </div>

            {/* Grid de proveedores */}
            {isLoading ? (
                <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                </div>
            ) : data?.proveedores && data.proveedores.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {data.proveedores.map((proveedor) => (
                        <div
                            key={proveedor.id}
                            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
                        >
                            {/* Header de tarjeta */}
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                                        <Users className="w-6 h-6 text-primary" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900">{proveedor.nombre}</h3>
                                        {proveedor.rif && (
                                            <p className="text-xs text-gray-500">RIF: {proveedor.rif}</p>
                                        )}
                                    </div>
                                </div>
                                <button
                                    onClick={() => handleEditar(proveedor.id)}
                                    className="p-2 text-gray-400 hover:text-primary hover:bg-gray-100 rounded-lg transition-colors"
                                >
                                    <Edit className="w-4 h-4" />
                                </button>
                            </div>

                            {/* Información de contacto */}
                            <div className="space-y-2">
                                {proveedor.nombre_contacto && (
                                    <div className="flex items-center gap-2 text-sm text-gray-600">
                                        <Users className="w-4 h-4" />
                                        <span>{proveedor.nombre_contacto}</span>
                                    </div>
                                )}
                                {proveedor.telefono && (
                                    <div className="flex items-center gap-2 text-sm text-gray-600">
                                        <Phone className="w-4 h-4" />
                                        <span>{proveedor.telefono}</span>
                                    </div>
                                )}
                                {proveedor.email && (
                                    <div className="flex items-center gap-2 text-sm text-gray-600">
                                        <Mail className="w-4 h-4" />
                                        <span className="truncate">{proveedor.email}</span>
                                    </div>
                                )}
                                {proveedor.direccion && (
                                    <div className="flex items-center gap-2 text-sm text-gray-600">
                                        <MapPin className="w-4 h-4" />
                                        <span className="truncate">{proveedor.direccion}</span>
                                    </div>
                                )}
                            </div>

                            {/* Footer */}
                            <div className="mt-4 pt-4 border-t border-gray-200">
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-gray-500">
                                        {proveedor.cantidad_productos || 0} productos
                                    </span>
                                    {proveedor.calificacion && (
                                        <div className="flex items-center gap-1">
                                            <span className="text-yellow-500">★</span>
                                            <span className="text-sm font-medium text-gray-700">
                                                {proveedor.calificacion.toFixed(1)}
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Términos de pago */}
                            {proveedor.terminos_pago && (
                                <div className="mt-3 px-3 py-2 bg-blue-50 rounded-lg">
                                    <p className="text-xs text-blue-700">
                                        <strong>Términos:</strong> {proveedor.terminos_pago}
                                    </p>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center h-64 bg-white rounded-xl shadow-sm border border-gray-200 text-gray-500">
                    <Users className="w-16 h-16 mb-4 text-gray-300" />
                    <p className="text-lg font-medium">No hay proveedores</p>
                    <p className="text-sm">Comienza agregando tu primer proveedor</p>
                </div>
            )}

            {/* Modal de formulario */}
            {modalAbierto && (
                <ProveedorFormModal
                    proveedorId={proveedorEditar}
                    onClose={() => setModalAbierto(false)}
                />
            )}
        </div>
    )
}
