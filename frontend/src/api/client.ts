/**
 * Cliente Axios configurado para la API.
 * Incluye interceptors para JWT y manejo de errores.
 */
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor para agregar token JWT
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Interceptor para manejar errores y refresh de token
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Si el error es 401 y no hemos intentado refrescar el token
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                if (refreshToken) {
                    const response = await axios.post(`${API_URL}/auth/refresh`, {}, {
                        headers: {
                            Authorization: `Bearer ${refreshToken}`,
                        },
                    });

                    const { access_token } = response.data;
                    localStorage.setItem('access_token', access_token);

                    // Reintentar la petición original
                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                    return apiClient(originalRequest);
                }
            } catch (refreshError) {
                // Si falla el refresh, limpiar todo y redirigir
                console.error('[Auth] Refresh fallido:', refreshError);
                localStorage.clear(); // Limpiar todo para estar seguros
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        // Si el error es 422 (Token inválido/malformado) o 401 sin refresh exitoso
        if (error.response?.status === 401 || error.response?.status === 422) {
            console.warn(`[Auth] Error ${error.response?.status} detectado. Cerrando sesión.`, {
                url: originalRequest.url,
                data: error.response?.data
            });

            // Limpiar localStorage (incluyendo auth-storage de Zustand)
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('usuario');
            localStorage.removeItem('auth-storage');

            // Redirigir si no estamos ya en login
            if (!window.location.pathname.includes('/login')) {
                window.location.href = '/login';
            }
            return Promise.reject(error);
        }

        // Mostrar detalles de validación si existen
        const data = error.response?.data || {};
        let mensaje = data.mensaje || data.message || error.message || 'Error desconocido';

        if (data.detalles) {
            // data.detalles puede ser un objeto {campo: [mensajes]}
            if (typeof data.detalles === 'object') {
                const partes: string[] = [];
                for (const [campo, msgs] of Object.entries<any>(data.detalles)) {
                    const textos = Array.isArray(msgs) ? msgs.join('; ') : String(msgs);
                    partes.push(`${campo}: ${textos}`);
                }
                mensaje = partes.join(' | ');
            } else if (Array.isArray(data.detalles)) {
                mensaje = data.detalles.join('; ');
            } else {
                mensaje = String(data.detalles);
            }
        } else if (data.error) {
            mensaje = data.error;
        }

        // Solo mostrar toast si la query/mutation no va a manejarlo manualmente
        // Usamos una convención: si el config tiene suppressToast: true, no mostramos toast aquí
        if (!originalRequest.suppressToast) {
            toast.error(mensaje);
        }

        return Promise.reject(error);
    }
);

export default apiClient;
