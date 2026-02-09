import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { X, Loader2 } from 'lucide-react'
import { useProveedor, useCrearProveedor, useActualizarProveedor } from '@/api/queries/proveedores.queries'
import type { Proveedor } from '@/types/api.types'

interface ProveedorFormModalProps {
    proveedorId: number | null
    onClose: () => void
}

export default function ProveedorFormModal({ proveedorId, onClose }: ProveedorFormModalProps) {
    const { data: proveedor, isLoading: cargandoProveedor } = useProveedor(proveedorId!)
    const crearProveedor = useCrearProveedor()
    const actualizarProveedor = useActualizarProveedor()

    const { register, handleSubmit, reset, formState: { errors } } = useForm<Partial<Proveedor>>()

    useEffect(() => {
        if (proveedor) {
            reset(proveedor)
        }
    }, [proveedor, reset])

    const onSubmit = (data: Partial<Proveedor>) => {
        if (proveedorId) {
            actualizarProveedor.mutate(
                { id: proveedorId, data },
                { onSuccess: onClose }
            )
        } else {
            crearProveedor.mutate(data, { onSuccess: onClose })
        }
    }

    const isPending = crearProveedor.isPending || actualizarProveedor.isPending

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <h2 className="text-2xl font-bold text-gray-900">
                        {proveedorId ? 'Editar Proveedor' : 'Nuevo Proveedor'}
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Formulario */}
                {cargandoProveedor && proveedorId ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                    </div>
                ) : (
                    <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
                        {/* Información básica */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Nombre de la Empresa *
                                </label>
                                <input
                                    {...register('nombre', { required: 'El nombre es requerido' })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                    placeholder="Distribuidora ABC"
                                />
                                {errors.nombre && (
                                    <p className="text-red-500 text-sm mt-1">{errors.nombre.message}</p>
                                )}
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Nombre de Contacto
                                </label>
                                <input
                                    {...register('nombre_contacto')}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                    placeholder="Juan Pérez"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    RIF (Venezuela) *
                                </label>
                                <input
                                    {...register('rif', {
                                        required: 'El RIF es requerido',
                                        pattern: {
                                            value: /^[JVG]-\d{8}-\d$/,
                                            message: 'Formato inválido (Ej: J-12345678-9)'
                                        }
                                    })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                    placeholder="J-12345678-9"
                                />
                                {errors.rif && (
                                    <p className="text-red-500 text-sm mt-1">{errors.rif.message}</p>
                                )}
                            </div>
                        </div>

                        {/* Contacto */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Teléfono
                                </label>
                                <input
                                    {...register('telefono', {
                                        pattern: {
                                            value: /^[\d\+\-\s\(\)]{7,20}$/,
                                            message: 'Formato de teléfono inválido'
                                        }
                                    })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                    placeholder="(809) 555-1234"
                                />
                                {errors.telefono && (
                                    <p className="text-red-500 text-sm mt-1">{errors.telefono.message}</p>
                                )}
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Email
                                </label>
                                <input
                                    type="email"
                                    {...register('email')}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                    placeholder="contacto@proveedor.com"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Dirección
                            </label>
                            <input
                                {...register('direccion')}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                placeholder="Calle Principal #123, Ciudad"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Términos de Pago
                            </label>
                            <input
                                {...register('terminos_pago')}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                placeholder="30 días, Contado, etc."
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Notas
                            </label>
                            <textarea
                                {...register('notas')}
                                rows={3}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                                placeholder="Notas adicionales sobre el proveedor..."
                            />
                        </div>

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
                                    proveedorId ? 'Actualizar' : 'Crear Proveedor'
                                )}
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    )
}
