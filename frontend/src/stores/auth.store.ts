/**
 * Store de autenticación usando Zustand.
 * Maneja el estado del usuario y tokens.
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Usuario } from '@/types/api.types';

interface AuthState {
    usuario: Usuario | null;
    accessToken: string | null;
    refreshToken: string | null;
    isAuthenticated: boolean;

    // Acciones
    setAuth: (usuario: Usuario, accessToken: string, refreshToken: string) => void;
    clearAuth: () => void;
    updateUsuario: (usuario: Partial<Usuario>) => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            usuario: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,

            setAuth: (usuario, accessToken, refreshToken) => {
                // Guardar en localStorage también para el interceptor de axios
                localStorage.setItem('access_token', accessToken);
                localStorage.setItem('refresh_token', refreshToken);
                localStorage.setItem('usuario', JSON.stringify(usuario));

                set({
                    usuario,
                    accessToken,
                    refreshToken,
                    isAuthenticated: true,
                });
            },

            clearAuth: () => {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('usuario');

                set({
                    usuario: null,
                    accessToken: null,
                    refreshToken: null,
                    isAuthenticated: false,
                });
            },

            updateUsuario: (usuarioActualizado) => {
                set((state) => {
                    if (!state.usuario) return state;

                    const nuevoUsuario = { ...state.usuario, ...usuarioActualizado };
                    localStorage.setItem('usuario', JSON.stringify(nuevoUsuario));

                    return {
                        usuario: nuevoUsuario,
                    };
                });
            },
        }),
        {
            name: 'auth-storage',
        }
    )
);
