import { Bell, LogOut, User, Menu, Check, AlertCircle } from 'lucide-react'
import { useAuthStore } from '@/stores/auth.store'
import { useLogout } from '@/api/queries/auth.queries'
import { useState, useRef, useEffect } from 'react'
import { useAlertas, useResolverAlerta } from '@/api/queries/alertas.queries'

export default function Navbar({ onMenuClick }: { onMenuClick?: () => void }) {
    const usuario = useAuthStore((state) => state.usuario)
    const logout = useLogout()
    const [showNotifications, setShowNotifications] = useState(false)
    const dropdownRef = useRef<HTMLDivElement>(null)

    const { data: alertas = [], isLoading } = useAlertas(true)
    const resolverAlerta = useResolverAlerta()

    // Cerrar dropdown al hacer click fuera
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setShowNotifications(false)
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    const handleResolve = (e: React.MouseEvent, id: number) => {
        e.stopPropagation()
        resolverAlerta.mutate({ id, notas: 'Resuelta desde el Navbar' })
    }

    return (
        <header className="bg-white border-b border-gray-200 px-4 md:px-6 py-4 relative z-50">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    {/* Botón de Hamburguesa para móvil */}
                    <button
                        onClick={onMenuClick}
                        className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg lg:hidden"
                    >
                        <Menu className="w-6 h-6" />
                    </button>

                    {/* Título de página */}
                    <div className="hidden sm:block">
                        <h2 className="text-xl md:text-2xl font-bold text-gray-900 truncate">
                            ¡Hola, {usuario?.nombre_completo.split(' ')[0]}!
                        </h2>
                    </div>
                </div>

                {/* Acciones */}
                <div className="flex items-center gap-4">
                    {/* Notificaciones */}
                    <div className="relative" ref={dropdownRef}>
                        <button
                            onClick={() => setShowNotifications(!showNotifications)}
                            className={`relative p-2 rounded-lg transition-colors ${showNotifications ? 'bg-gray-100 text-primary' : 'text-gray-600 hover:bg-gray-100'
                                }`}
                            title="Ver notificaciones"
                        >
                            <Bell className="w-5 h-5" />
                            {alertas.length > 0 && (
                                <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center bg-red-500 text-[10px] font-bold text-white rounded-full">
                                    {alertas.length}
                                </span>
                            )}
                        </button>

                        {/* Dropdown de Notificaciones */}
                        {showNotifications && (
                            <div className="absolute right-0 mt-2 w-80 md:w-96 bg-white rounded-xl shadow-xl border border-gray-200 overflow-hidden transform transition-all duration-200 ease-out origin-top-right">
                                <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50">
                                    <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                                        <Bell className="w-4 h-4 text-primary" />
                                        Notificaciones
                                    </h3>
                                    <span className="text-xs font-medium px-2 py-0.5 bg-primary/10 text-primary rounded-full">
                                        {alertas.length} nuevas
                                    </span>
                                </div>
                                <div className="max-h-[70vh] overflow-y-auto">
                                    {isLoading ? (
                                        <div className="p-8 text-center text-gray-500">
                                            <div className="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mx-auto mb-2"></div>
                                            <p className="text-sm">Cargando...</p>
                                        </div>
                                    ) : alertas.length > 0 ? (
                                        <div className="divide-y divide-gray-50">
                                            {alertas.map((alerta: any) => (
                                                <div key={alerta.id} className="p-4 hover:bg-gray-50 transition-colors group">
                                                    <div className="flex items-start gap-3">
                                                        <div className={`mt-1 p-2 rounded-lg ${alerta.prioridad === 'CRITICA' ? 'bg-red-100 text-red-600' :
                                                            alerta.prioridad === 'ALTA' ? 'bg-orange-100 text-orange-600' : 'bg-blue-100 text-blue-600'
                                                            }`}>
                                                            <AlertCircle className="w-4 h-4" />
                                                        </div>
                                                        <div className="flex-1">
                                                            <div className="flex items-center justify-between mb-0.5">
                                                                <p className="text-xs font-medium text-gray-500">
                                                                    {new Date(alerta.creado_en).toLocaleDateString()}
                                                                </p>
                                                                <button
                                                                    onClick={(e) => handleResolve(e, alerta.id)}
                                                                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-green-100 text-green-600 rounded transition-all"
                                                                    title="Marcar como resuelta"
                                                                >
                                                                    <Check className="w-3.5 h-3.5" />
                                                                </button>
                                                            </div>
                                                            <p className="text-sm font-semibold text-gray-900 leading-tight">{alerta.titulo}</p>
                                                            <p className="text-xs text-gray-600 mt-1 line-clamp-2">{alerta.mensaje}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="p-12 text-center text-gray-500">
                                            <div className="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-3">
                                                <Check className="w-6 h-6 text-gray-300" />
                                            </div>
                                            <p className="text-sm font-medium">¡Todo al día!</p>
                                            <p className="text-xs mt-1">No tienes alertas pendientes</p>
                                        </div>
                                    )}
                                </div>
                                {alertas.length > 0 && (
                                    <div className="p-3 bg-gray-50 border-t border-gray-100 text-center">
                                        <button
                                            onClick={() => window.location.href = '/reportes'}
                                            className="text-xs font-semibold text-primary hover:underline"
                                        >
                                            Ver todos los reportes
                                        </button>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Perfil */}
                    <div className="flex items-center gap-2 md:gap-3 px-2 md:px-3 py-1.5 md:py-2 bg-gray-100 rounded-lg">
                        <div className="w-7 h-7 md:w-8 md:h-8 bg-primary rounded-full flex items-center justify-center shadow-sm">
                            <User className="w-4 h-4 md:w-5 md:h-5 text-white" />
                        </div>
                        <div className="text-xs md:text-sm hidden xs:block">
                            <p className="font-medium text-gray-900 max-w-[100px] truncate">{usuario?.nombre_completo}</p>
                            <p className="text-[10px] md:text-xs text-gray-500">{usuario?.rol}</p>
                        </div>
                    </div>

                    {/* Logout */}
                    <button
                        onClick={() => logout.mutate()}
                        className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                        title="Cerrar sesión"
                    >
                        <LogOut className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </header>
    )
}
