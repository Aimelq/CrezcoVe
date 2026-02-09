/**
 * Queries de React Query para proveedores.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import apiClient from '../client';
import type { Proveedor } from '@/types/api.types';

export const useProveedores = () => {
    return useQuery({
        queryKey: ['proveedores'],
        queryFn: async () => {
            const response = await apiClient.get<{ proveedores: Proveedor[] }>('/proveedores');
            return response.data;
        },
    });
};

export const useProveedor = (id: number) => {
    return useQuery({
        queryKey: ['proveedor', id],
        queryFn: async () => {
            const response = await apiClient.get<Proveedor>(`/proveedores/${id}`);
            return response.data;
        },
        enabled: !!id,
    });
};

export const useCrearProveedor = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (data: Partial<Proveedor>) => {
            const response = await apiClient.post<Proveedor>('/proveedores', data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['proveedores'] });
            toast.success('Proveedor creado exitosamente');
        },
    });
};

export const useActualizarProveedor = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({ id, data }: { id: number; data: Partial<Proveedor> }) => {
            const response = await apiClient.put<Proveedor>(`/proveedores/${id}`, data);
            return response.data;
        },
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['proveedores'] });
            queryClient.invalidateQueries({ queryKey: ['proveedor', variables.id] });
            toast.success('Proveedor actualizado exitosamente');
        },
    });
};

export const usePedidoSugerido = (id: number) => {
    return useQuery({
        queryKey: ['pedido-sugerido', id],
        queryFn: async () => {
            const response = await apiClient.get(`/proveedores/${id}/pedido-sugerido`);
            return response.data;
        },
        enabled: !!id,
    });
};
