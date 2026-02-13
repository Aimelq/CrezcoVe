import { useEffect, useState } from 'react'
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from './stores/auth.store'
import { apiClient } from './api/client'

// Páginas
import LoginPage from './pages/Auth/LoginPage'
import SetupPage from './pages/Auth/SetupPage'
import DashboardPage from './pages/Dashboard/DashboardPage'
import ProductosPage from './pages/Products/ProductosPage'
import InventarioPage from './pages/Inventory/InventarioPage'
import ProveedoresPage from './pages/Suppliers/ProveedoresPage'
import ReportesPage from './pages/Reports/ReportesPage'
import ReporteVentasPage from './pages/Reports/ReporteVentasPage'
import ProfilePage from './pages/Profile/ProfilePage'
import UsuariosPage from './pages/Admin/UsuariosPage'
import VerificarEmailPage from './pages/Auth/VerificarEmailPage'
import LotesPage from './pages/Inventory/LotesPage'
import SaludFinancieraPage from './pages/BusinessIntelligence/SaludFinancieraPage'

// Layout
import MainLayout from './components/layout/MainLayout'

// Componente de ruta protegida
function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
    if (!isAuthenticated) return <Navigate to="/login" replace />
    return <>{children}</>
}

function App() {
    const navigate = useNavigate()
    const location = useLocation()
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const checkSystemStatus = async () => {
            try {
                // Solo verificar si no estamos ya en setup
                if (location.pathname === '/setup') {
                    setIsLoading(false)
                    return
                }

                const { data } = await apiClient.get('/setup/status')

                if (data.necesita_setup) {
                    navigate('/setup', { replace: true })
                }
            } catch (error) {
                console.error('Error verificando estado del sistema:', error)
            } finally {
                setIsLoading(false)
            }
        }

        checkSystemStatus()
    }, []) // Se ejecuta solo al montar

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        )
    }

    return (
        <Routes>
            {/* Ruta de configuración inicial */}
            <Route path="/setup" element={<SetupPage />} />

            {/* Rutas públicas */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/verificar-email" element={<VerificarEmailPage />} />

            {/* Rutas protegidas */}
            <Route
                path="/"
                element={
                    <ProtectedRoute>
                        <MainLayout />
                    </ProtectedRoute>
                }
            >
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="productos" element={<ProductosPage />} />
                <Route path="salud-financiera" element={<SaludFinancieraPage />} />
                <Route path="inventario" element={<InventarioPage />} />
                <Route path="proveedores" element={<ProveedoresPage />} />
                <Route path="reportes" element={<ReportesPage />} />
                <Route path="reportes/ventas" element={<ReporteVentasPage />} />
                <Route path="configuracion" element={<ProfilePage />} />
                <Route path="usuarios" element={<UsuariosPage />} />
                <Route path="lotes" element={<LotesPage />} />
            </Route>

            {/* Ruta 404 */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
    )
}

export default App
