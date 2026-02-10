/**
 * Queries de React Query para inventario.
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import apiClient from '../client';
import type { IngresoInventarioRequest, SalidaInventarioRequest, AjusteInventarioRequest, VentaMultipleRequest, TasaCambio } from '@/types/api.types';

export const useRegistrarIngreso = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (data: IngresoInventarioRequest) => {
            const response = await apiClient.post('/inventario/ingreso', data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['productos'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard'] });
            toast.success('Ingreso registrado exitosamente');
        },
    });
};

export const useRegistrarSalida = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (data: SalidaInventarioRequest) => {
            const response = await apiClient.post('/inventario/salida', data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['productos'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard'] });
            toast.success('Venta registrada exitosamente');
        },
    });
};

export const useRegistrarVentaMultiple = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (data: VentaMultipleRequest) => {
            const response = await apiClient.post('/inventario/venta-multiple', data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['productos'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard'] });
            toast.success('Venta múltiple registrada exitosamente');
        },
    });
};

export const useRegistrarAjuste = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (data: AjusteInventarioRequest) => {
            const response = await apiClient.post('/inventario/ajuste', data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['productos'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard'] });
            toast.success('Ajuste registrado exitosamente');
        },
    });
};

export const useTasaCambio = (autoActualizar = false) => {
    const queryClient = useQueryClient();

    const query = useMutation({
        mutationFn: async (tasa: number) => {
            const response = await apiClient.post('/inventario/tasa-cambio', { tasa });
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['tasa-cambio'] });
            toast.success('Tasa de cambio actualizada');
        },
    });

    return {
        actualizarTasa: query.mutate,
        isUpdating: query.isPending,
    };
};

export const useGetTasaCambio = (actualizar = false) => {
    return useQuery({
        queryKey: ['tasa-cambio', actualizar],
        queryFn: async () => {
            const response = await apiClient.get(`/inventario/tasa-cambio?actualizar=${actualizar}`);
            return response.data as TasaCambio;
        },
        staleTime: 1000 * 60 * 60, // 1 hora
    });
};
export const useDesempacar = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (data: { producto_id: number; cantidad: number }) => {
            const response = await apiClient.post('/inventario/desempacar', data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['productos'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard'] });
            toast.success('Fraccionamiento completado exitosamente');
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.message || 'Error al desempacar producto');
        }
    });
};
