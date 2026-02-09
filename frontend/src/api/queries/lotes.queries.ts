import { useQuery } from '@tanstack/react-query'
import apiClient from '../client'
import type { Lote } from '@/types/api.types'

export const lotesKeys = {
    all: ['lotes'] as const,
    lista: () => [...lotesKeys.all, 'lista'] as const,
    producto: (id: number) => [...lotesKeys.all, 'producto', id] as const,
}

export function useLotes() {
    return useQuery({
        queryKey: lotesKeys.lista(),
        queryFn: async () => {
            const { data } = await apiClient.get<Lote[]>('/lotes/')
            return data
        }
    })
}

export function useLotesProducto(productoId: number) {
    return useQuery({
        queryKey: lotesKeys.producto(productoId),
        queryFn: async () => {
            const { data } = await apiClient.get<Lote[]>(`/lotes/producto/${productoId}`)
            return data
        },
        enabled: !!productoId
    })
}
