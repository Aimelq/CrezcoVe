/**
 * Queries de React Query para productos.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import apiClient from '../client';
import type { Producto, PaginatedResponse } from '@/types/api.types';

export const useProductos = (params?: {
    buscar?: string;
    categoria_id?: number;
    stock_bajo?: boolean;
    pagina?: number;
    por_pagina?: number;
}) => {
    return useQuery({
        queryKey: ['productos', params],
        queryFn: async () => {
            const response = await apiClient.get<PaginatedResponse<Producto>>('/productos', {
                params,
            });
            return response.data;
        },
    });
};

export const useProducto = (id: number) => {
    return useQuery({
        queryKey: ['producto', id],
        queryFn: async () => {
            const response = await apiClient.get<Producto>(`/productos/${id}`);
            return response.data;
        },
        enabled: !!id,
    });
};

export const useCrearProducto = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (data: Partial<Producto>) => {
            const response = await apiClient.post<Producto>('/productos', data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['productos'] });
            toast.success('Producto creado exitosamente');
        },
    });
};

export const useActualizarProducto = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({ id, data }: { id: number; data: Partial<Producto> }) => {
            const response = await apiClient.put<Producto>(`/productos/${id}`, data);
            return response.data;
        },
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['productos'] });
            queryClient.invalidateQueries({ queryKey: ['producto', variables.id] });
            toast.success('Producto actualizado exitosamente');
        },
    });
};

export const useEliminarProducto = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (id: number) => {
            await apiClient.delete(`/productos/${id}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['productos'] });
            toast.success('Producto eliminado exitosamente');
        },
    });
};

export const usePrediccionAgotamiento = (id: number) => {
    return useQuery({
        queryKey: ['prediccion', id],
        queryFn: async () => {
            const response = await apiClient.get(`/productos/${id}/prediccion-agotamiento`);
            return response.data;
        },
        enabled: !!id,
    });
};
