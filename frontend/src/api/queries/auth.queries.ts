/**
 * Queries de React Query para autenticación.
 */
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import apiClient from '../client';
import { useAuthStore } from '@/stores/auth.store';
import type { LoginRequest, RegistroRequest, AuthResponse } from '@/types/api.types';

export const useLogin = () => {
    const navigate = useNavigate();
    const setAuth = useAuthStore((state) => state.setAuth);

    return useMutation({
        mutationFn: async (data: LoginRequest): Promise<AuthResponse> => {
            const response = await apiClient.post('/auth/login', data, {
                // @ts-ignore - suppressToast es una propiedad custom
                suppressToast: true
            });
            return response.data as AuthResponse;
        },
        onSuccess: (data: AuthResponse) => {
            setAuth(data.usuario, data.access_token, data.refresh_token);
            toast.success(`¡Bienvenido, ${data.usuario.nombre_completo}!`);
            navigate('/dashboard');
        },
        onError: (error: any) => {
            const mensaje = error.response?.data?.mensaje || error.response?.data?.message || 'Error al iniciar sesión';
            if (error.response?.status === 403 && mensaje.includes('verificar')) {
                toast.warning(mensaje, { duration: 6000 });
            } else {
                toast.error(mensaje === 'Credenciales inválidas' ? 'Correo o contraseña incorrectos' : mensaje);
            }
        },
    });
};

export const useRegistro = () => {
    const navigate = useNavigate();
    const setAuth = useAuthStore((state) => state.setAuth);

    return useMutation({
        mutationFn: async (data: RegistroRequest) => {
            const response = await apiClient.post<AuthResponse>('/auth/registro', data, {
                // @ts-ignore - suppressToast es una propiedad custom
                suppressToast: true
            });
            return response.data;
        },
        onSuccess: (data: any) => {
            if (data.access_token) {
                setAuth(data.usuario, data.access_token, data.refresh_token);
                toast.success('¡Registro exitoso!');
                navigate('/dashboard');
            } else {
                toast.success(data.mensaje || 'Registro exitoso. Por favor verifica tu correo.', { duration: 8000 });
                navigate('/login');
            }
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.mensaje || 'Error al registrar usuario');
        }
    });
};

export const useLogout = () => {
    const navigate = useNavigate();
    const clearAuth = useAuthStore((state) => state.clearAuth);
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async () => {
            await apiClient.post('/auth/logout');
        },
        onSuccess: () => {
            clearAuth();
            queryClient.clear();
            toast.success('Sesión cerrada');
            navigate('/login');
        },
    });
};

export const useVerificarEmail = () => {
    const navigate = useNavigate();

    return useMutation({
        mutationFn: async (token: string) => {
            const response = await apiClient.get(`/auth/verificar-email?token=${token}`);
            return response.data;
        },
        onSuccess: (data: any) => {
            toast.success(data.mensaje || 'Email verificado correctamente');
            navigate('/login');
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.mensaje || 'Error al verificar el email. El token podría haber expirado.');
        }
    });
};
