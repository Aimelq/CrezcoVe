import { useState, useEffect } from 'react'
import { apiClient } from '@/api/client'
import { toast } from 'sonner'
import { Users, UserPlus, Trash2, Mail, Phone, Shield, Search, X } from 'lucide-react'

interface Usuario {
    id: number
    nombre_completo: string
    email: string
    rol: string
    esta_activo: boolean
    telefono?: string
    telegram_chat_id?: string
}

export default function UsuariosPage() {
    const [usuarios, setUsuarios] = useState<Usuario[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [searchQuery, setSearchQuery] = useState('')

    const [newUsuario, setNewUsuario] = useState({
        nombre_completo: '',
        email: '',
        password: '',
        rol: 'EMPLEADO',
        telefono: ''
    })

    const fetchUsuarios = async () => {
        setIsLoading(true)
        try {
            const { data } = await apiClient.get('/usuarios')
            setUsuarios(data)
        } catch (error) {
            console.error('Error fetching usuarios:', error)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        fetchUsuarios()
    }, [])

    const handleCreateUsuario = async (e: React.FormEvent) => {
        e.preventDefault()
        // Validación básica en cliente para teléfono
        const telefonoValido = newUsuario.telefono === '' || /^[\d\+\-\s\(\)]{7,20}$/.test(newUsuario.telefono)
        if (!telefonoValido) {
            toast.error('Formato de teléfono inválido')
            return
        }

        try {
            await apiClient.post('/auth/registro', newUsuario)
            setIsModalOpen(false)
            setNewUsuario({ nombre_completo: '', email: '', password: '', rol: 'EMPLEADO', telefono: '' })
            fetchUsuarios()
        } catch (error) {
            console.error('Error creating usuario:', error)
            // El cliente `apiClient` ya muestra toasts con detalles de validación
        }
    }

    const handleToggleStatus = async (id: number, currentStatus: boolean) => {
        if (!confirm(`¿Está seguro de que desea ${currentStatus ? 'desactivar' : 'activar'} a este usuario?`)) return
        try {
            await apiClient.put(`/usuarios/${id}`, { esta_activo: !currentStatus })
            fetchUsuarios()
        } catch (error) {
            console.error('Error updating status:', error)
        }
    }

    const filteredUsuarios = usuarios.filter(u =>
        u.nombre_completo.toLowerCase().includes(searchQuery.toLowerCase()) ||
        u.email.toLowerCase().includes(searchQuery.toLowerCase())
    )

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Gestión de Empleados</h1>
                    <p className="text-sm text-gray-500">Administra los accesos al sistema</p>
                </div>
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="flex items-center justify-center gap-2 bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors"
                >
                    <UserPlus className="w-5 h-5" />
                    Registrar Empleado
                </button>
            </div>

            {/* Barra de búsqueda */}
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                    type="text"
                    placeholder="Buscar por nombre o correo..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                />
            </div>

            {/* Tabla de Usuarios */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50 border-b border-gray-200">
                            <tr>
                                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Usuario</th>
                                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Rol</th>
                                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Estado</th>
                                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {isLoading ? (
                                <tr>
                                    <td colSpan={4} className="px-6 py-10 text-center text-gray-500">
                                        Cargando usuarios...
                                    </td>
                                </tr>
                            ) : filteredUsuarios.length === 0 ? (
                                <tr>
                                    <td colSpan={4} className="px-6 py-10 text-center text-gray-500">
                                        No se encontraron usuarios
                                    </td>
                                </tr>
                            ) : filteredUsuarios.map((u) => (
                                <tr key={u.id} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                                                <Users className="w-5 h-5 text-gray-600" />
                                            </div>
                                            <div>
                                                <p className="font-medium text-gray-900">{u.nombre_completo}</p>
                                                <div className="flex items-center gap-2 text-xs text-gray-500">
                                                    <Mail className="w-3 h-3" />
                                                    {u.email}
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium w-fit border">
                                            <Shield className="w-3 h-3" />
                                            {u.rol}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={cn(
                                            "px-2.5 py-0.5 rounded-full text-xs font-medium",
                                            u.esta_activo ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                                        )}>
                                            {u.esta_activo ? 'Activo' : 'Inactivo'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <button
                                            onClick={() => handleToggleStatus(u.id, u.esta_activo)}
                                            className={cn(
                                                "p-2 rounded-lg transition-colors",
                                                u.esta_activo ? "text-red-600 hover:bg-red-50" : "text-green-600 hover:bg-green-50"
                                            )}
                                            title={u.esta_activo ? 'Desactivar' : 'Activar'}
                                        >
                                            <Trash2 className="w-5 h-5" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Modal de Registro */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[60] p-4">
                    <div className="bg-white rounded-xl w-full max-w-md shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
                        <div className="p-6 border-b border-gray-100 flex items-center justify-between">
                            <h3 className="text-xl font-bold">Registrar Nuevo Empleado</h3>
                            <button onClick={() => setIsModalOpen(false)} className="text-gray-400 hover:text-gray-600">
                                <X className="w-6 h-6" />
                            </button>
                        </div>
                        <form onSubmit={handleCreateUsuario} className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Nombre Completo</label>
                                <input
                                    type="text"
                                    required
                                    className="w-full px-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-primary"
                                    value={newUsuario.nombre_completo}
                                    onChange={(e) => setNewUsuario({ ...newUsuario, nombre_completo: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Correo Electrónico</label>
                                <input
                                    type="email"
                                    required
                                    className="w-full px-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-primary"
                                    value={newUsuario.email}
                                    onChange={(e) => setNewUsuario({ ...newUsuario, email: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
                                <input
                                    type="text"
                                    className="w-full px-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-primary"
                                    value={newUsuario.telefono}
                                    onChange={(e) => setNewUsuario({ ...newUsuario, telefono: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña Temporal</label>
                                <input
                                    type="password"
                                    required
                                    className="w-full px-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-primary"
                                    value={newUsuario.password}
                                    onChange={(e) => setNewUsuario({ ...newUsuario, password: e.target.value })}
                                />
                            </div>
                            <div className="pt-4">
                                <button type="submit" className="w-full bg-primary text-white py-3 rounded-lg font-bold hover:bg-primary/90 transition-colors">
                                    Registrar Usuario
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    )
}

function cn(...classes: any[]) {
    return classes.filter(Boolean).join(' ')
}
