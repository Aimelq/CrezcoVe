import { useEffect, useRef } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useVerificarEmail } from '@/api/queries/auth.queries'
import { CheckCircle, XCircle, Loader2 } from 'lucide-react'

export default function VerificarEmailPage() {
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()
    const token = searchParams.get('token')
    const hasAttempted = useRef(false)
    const { mutate: verificar, isPending, isSuccess, isError } = useVerificarEmail()

    useEffect(() => {
        if (token && !hasAttempted.current) {
            hasAttempted.current = true
            verificar(token)
        }
    }, [token, verificar])

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
            <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center border border-gray-100">
                {isPending && (
                    <div className="space-y-4">
                        <div className="flex justify-center">
                            <Loader2 className="w-16 h-16 text-primary animate-spin" />
                        </div>
                        <h2 className="text-2xl font-bold text-gray-900">Verificando tu cuenta</h2>
                        <p className="text-gray-600">Espera un momento mientras validamos tu correo electrónico...</p>
                    </div>
                )}

                {isSuccess && (
                    <div className="space-y-6">
                        <div className="flex justify-center">
                            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
                                <CheckCircle className="w-12 h-12 text-green-600" />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <h2 className="text-2xl font-bold text-gray-900">¡Email Verificado!</h2>
                            <p className="text-gray-600">Tu cuenta ha sido activada correctamente. Ya puedes acceder al sistema con tus credenciales.</p>
                        </div>
                        <button
                            onClick={() => navigate('/login')}
                            className="w-full py-3 px-4 bg-primary text-white font-bold rounded-xl hover:bg-primary/90 transition-all shadow-lg shadow-primary/20"
                        >
                            Ir al Inicio de Sesión
                        </button>
                    </div>
                )}

                {isError && (
                    <div className="space-y-6">
                        <div className="flex justify-center">
                            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center">
                                <XCircle className="w-12 h-12 text-red-600" />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <h2 className="text-2xl font-bold text-gray-900">Error de Verificación</h2>
                            <p className="text-gray-600">El token de verificación es inválido o ha expirado. Por favor, intenta iniciar sesión para recibir un nuevo enlace.</p>
                        </div>
                        <button
                            onClick={() => navigate('/login')}
                            className="w-full py-3 px-4 bg-gray-900 text-white font-bold rounded-xl hover:bg-gray-800 transition-all"
                        >
                            Regresar al Login
                        </button>
                    </div>
                )}

                {!token && !isPending && !isSuccess && !isError && (
                    <div className="space-y-4">
                        <XCircle className="w-16 h-16 text-red-500 mx-auto" />
                        <h2 className="text-2xl font-bold text-gray-900">Token no encontrado</h2>
                        <p className="text-gray-600">No se proporcionó un token de verificación válido.</p>
                        <button
                            onClick={() => navigate('/login')}
                            className="text-primary font-medium hover:underline"
                        >
                            Volver al login
                        </button>
                    </div>
                )}
            </div>
        </div>
    )
}
