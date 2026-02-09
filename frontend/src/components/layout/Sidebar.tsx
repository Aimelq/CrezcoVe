import { NavLink } from 'react-router-dom'
import {
    LayoutDashboard,
    Package,
    ArrowLeftRight,
    Users,
    FileText,
    Box,
    X,
    TrendingUp,
    Settings
} from 'lucide-react'
import { useAuthStore } from '@/stores/auth.store'
import { cn } from '@/lib/utils'
import Logo from '../common/Logo'

const menuItems = [
    {
        title: 'Dashboard',
        icon: LayoutDashboard,
        path: '/dashboard',
    },
    {
        title: 'Productos',
        icon: Package,
        path: '/productos',
    },
    {
        title: 'Salud Financiera',
        icon: TrendingUp,
        path: '/salud-financiera',
        roles: ['DUENO']
    },
    {
        title: 'Inventario',
        icon: ArrowLeftRight,
        path: '/inventario',
    },
    {
        title: 'Lotes',
        icon: Box,
        path: '/lotes',
    },
    {
        title: 'Proveedores',
        icon: Users,
        path: '/proveedores',
        roles: ['DUENO']
    },
    {
        title: 'Usuarios',
        icon: Users,
        path: '/usuarios',
        roles: ['DUENO']
    },
    {
        title: 'Configuración',
        icon: Settings,
        path: '/configuracion',
    },
    {
        title: 'Reportes',
        icon: FileText,
        path: '/reportes',
        roles: ['DUENO']
    },
]

export default function Sidebar({ isOpen, onClose }: { isOpen?: boolean, onClose?: () => void }) {
    const usuario = useAuthStore((state) => state.usuario)

    const filteredItems = menuItems.filter(item =>
        !item.roles || (usuario && item.roles.includes(usuario.rol))
    )

    return (
        <>
            {/* Overlay para móvil */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-[55] lg:hidden"
                    onClick={onClose}
                />
            )}

            <aside className={cn(
                "fixed inset-y-0 left-0 z-[60] w-64 bg-white border-r border-gray-200 flex flex-col transition-transform lg:static lg:translate-x-0",
                !isOpen && "-translate-x-full"
            )}>
                {/* Logo */}
                <div className="p-6 border-b border-gray-200 flex items-center justify-between">
                    <Logo size="sm" />

                    {/* Botón cerrar para móvil */}
                    <button
                        onClick={onClose}
                        className="p-1 text-gray-400 hover:text-gray-600 lg:hidden"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Navegación */}
                <nav className="flex-1 p-4 space-y-1">
                    {filteredItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            onClick={onClose}
                            className={({ isActive }) =>
                                cn(
                                    'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
                                    'hover:bg-gray-100',
                                    isActive
                                        ? 'bg-primary text-white hover:bg-primary/90'
                                        : 'text-gray-700'
                                )
                            }
                        >
                            <item.icon className="w-5 h-5" />
                            <span className="font-medium">{item.title}</span>
                        </NavLink>
                    ))}
                </nav>

                {/* Footer */}
                <div className="p-4 border-t border-gray-200">
                    <p className="text-xs text-gray-500 text-center">
                        v1.0.0 - Sistema de Inventario
                    </p>
                </div>
            </aside>
        </>
    )
}
