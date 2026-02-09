import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../client'

export const useAlertas = (soloActivas = true) => {
    return useQuery({
        queryKey: ['alertas', soloActivas],
        queryFn: async () => {
            const { data } = await apiClient.get('/alertas', {
                params: { solo_activas: soloActivas }
            })
            return data
        }
    })
}

export const useResolverAlerta = () => {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: async ({ id, notas }: { id: number; notas?: string }) => {
            const { data } = await apiClient.post(`/alertas/${id}/resolver`, { notas })
            return data
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['alertas'] })
            queryClient.invalidateQueries({ queryKey: ['alertas-activas'] })
            queryClient.invalidateQueries({ queryKey: ['dashboard'] })
        }
    })
}
