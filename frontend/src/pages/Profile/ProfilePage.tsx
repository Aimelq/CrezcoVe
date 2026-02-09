import { useState, useEffect } from 'react'
import { useAuthStore } from '@/stores/auth.store'
import { apiClient } from '@/api/client'
import { User, Key, Save, AlertCircle, CheckCircle } from 'lucide-react'

export default function ProfilePage() {
    const usuario = useAuthStore((state) => state.usuario)
    const updateUsuario = useAuthStore((state) => state.updateUsuario)

    const [profileData, setProfileData] = useState({
        nombre_completo: '',
        email: '',
        telefono: '',
        telegram_chat_id: ''
    })

    const [passwords, setPasswords] = useState({
        password_actual: '',
        password_nuevo: '',
        confirm_password: ''
    })

    const [status, setStatus] = useState<{ type: 'success' | 'error', message: string } | null>(null)
    const [isSaving, setIsSaving] = useState(false)

    useEffect(() => {
        if (usuario) {
            setProfileData({
                nombre_completo: usuario.nombre_completo || '',
                email: usuario.email || '',
                telefono: usuario.telefono || '',
                telegram_chat_id: usuario.telegram_chat_id || ''
            })
        }
    }, [usuario])

    const handleProfileSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsSaving(true)
        setStatus(null)
        try {
            const { data } = await apiClient.put('/auth/perfil', profileData)
            updateUsuario(data)
            setStatus({ type: 'success', message: 'Perfil actualizado correctamente' })
        } catch (error: any) {
            setStatus({ type: 'error', message: error.response?.data?.mensaje || 'Error al actualizar perfil' })
        } finally {
            setIsSaving(false)
        }
    }

    const handlePasswordSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (passwords.password_nuevo !== passwords.confirm_password) {
            setStatus({ type: 'error', message: 'Las contraseñas no coinciden' })
            return
        }

        setIsSaving(true)
        setStatus(null)
        try {
            await apiClient.post('/auth/cambiar-password', {
                password_actual: passwords.password_actual,
                password_nuevo: passwords.password_nuevo
            })
            setStatus({ type: 'success', message: 'Contraseña actualizada correctamente' })
            setPasswords({ password_actual: '', password_nuevo: '', confirm_password: '' })
        } catch (error: any) {
            setStatus({ type: 'error', message: error.response?.data?.mensaje || 'Error al cambiar contraseña' })
        } finally {
            setIsSaving(false)
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-gray-900">Configuración de Cuenta</h1>
            </div>

            {status && (
                <div className={cn(
                    "p-4 rounded-lg flex items-center gap-3",
                    status.type === 'success' ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"
                )}>
                    {status.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                    <p className="text-sm font-medium">{status.message}</p>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Información de Perfil */}
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-6">
                        <User className="w-6 h-6 text-primary" />
                        <h2 className="text-lg font-semibold">Información Personal</h2>
                    </div>

                    <form onSubmit={handleProfileSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre Completo</label>
                            <input
                                type="text"
                                value={profileData.nombre_completo}
                                onChange={(e) => setProfileData({ ...profileData, nombre_completo: e.target.value })}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Correo Electrónico</label>
                            <input
                                type="email"
                                value={profileData.email}
                                onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                                required
                            />
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
                                <input
                                    type="text"
                                    value={profileData.telefono}
                                    onChange={(e) => setProfileData({ ...profileData, telefono: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">ID Telegram (Opcional)</label>
                                <input
                                    type="text"
                                    value={profileData.telegram_chat_id}
                                    onChange={(e) => setProfileData({ ...profileData, telegram_chat_id: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                                    placeholder="Ej: 123456789"
                                />
                            </div>
                        </div>
                        <button
                            type="submit"
                            disabled={isSaving}
                            className="w-full flex items-center justify-center gap-2 bg-primary text-white py-2 px-4 rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                        >
                            <Save className="w-5 h-5" />
                            {isSaving ? 'Guardando...' : 'Guardar Cambios'}
                        </button>
                    </form>
                </div>

                {/* Cambio de Contraseña */}
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-6">
                        <Key className="w-6 h-6 text-primary" />
                        <h2 className="text-lg font-semibold">Seguridad</h2>
                    </div>

                    <form onSubmit={handlePasswordSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña Actual</label>
                            <input
                                type="password"
                                value={passwords.password_actual}
                                onChange={(e) => setPasswords({ ...passwords, password_actual: e.target.value })}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                                required
                            />
                        </div>
                        <hr className="my-4" />
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Nueva Contraseña</label>
                            <input
                                type="password"
                                value={passwords.password_nuevo}
                                onChange={(e) => setPasswords({ ...passwords, password_nuevo: e.target.value })}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                                required
                                minLength={6}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Confirmar Nueva Contraseña</label>
                            <input
                                type="password"
                                value={passwords.confirm_password}
                                onChange={(e) => setPasswords({ ...passwords, confirm_password: e.target.value })}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={isSaving}
                            className="w-full flex items-center justify-center gap-2 bg-gray-900 text-white py-2 px-4 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50"
                        >
                            <Save className="w-5 h-5" />
                            {isSaving ? 'Actualizando...' : 'Actualizar Contraseña'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    )
}

function cn(...classes: any[]) {
    return classes.filter(Boolean).join(' ')
}
