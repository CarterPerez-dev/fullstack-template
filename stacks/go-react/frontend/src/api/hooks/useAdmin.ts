/**
 * ©AngelaMos | 2026
 * useAdmin.ts
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { userListResponseSchema, userResponseSchema } from '@/api/types'
import { API_ENDPOINTS, PAGINATION, QUERY_KEYS } from '@/config'
import { apiClient } from '@/core/api'

export const adminQueries = {
  all: () => QUERY_KEYS.ADMIN.ALL,
  users: {
    all: () => QUERY_KEYS.ADMIN.USERS.ALL(),
    list: (page: number, size: number) => QUERY_KEYS.ADMIN.USERS.LIST(page, size),
    byId: (id: string) => QUERY_KEYS.ADMIN.USERS.BY_ID(id),
  },
} as const

export function useAdminUsers(params: { page?: number; size?: number } = {}) {
  const page = params.page ?? PAGINATION.DEFAULT_PAGE
  const size = params.size ?? PAGINATION.DEFAULT_SIZE
  return useQuery({
    queryKey: adminQueries.users.list(page, size),
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.ADMIN.USERS.LIST, {
        params: { page, page_size: size },
      })
      return userListResponseSchema.parse(response.data)
    },
  })
}

export function useAdminUser(id: string) {
  return useQuery({
    queryKey: adminQueries.users.byId(id),
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.ADMIN.USERS.BY_ID(id))
      return userResponseSchema.parse(response.data)
    },
    enabled: id.length > 0,
  })
}

export function useAdminUpdateUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (params: { id: string; role: 'user' | 'admin' }) => {
      const response = await apiClient.put(
        `${API_ENDPOINTS.ADMIN.USERS.UPDATE(params.id)}/role`,
        { role: params.role }
      )
      return userResponseSchema.parse(response.data)
    },
    onSuccess: () => toast.success('Role updated'),
    onError: (error: Error) => toast.error(error.message),
    onSettled: () =>
      queryClient.invalidateQueries({ queryKey: adminQueries.all() }),
  })
}

export function useAdminDeleteUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(API_ENDPOINTS.ADMIN.USERS.DELETE(id))
    },
    onSuccess: () => toast.success('User deleted'),
    onError: (error: Error) => toast.error(error.message),
    onSettled: () =>
      queryClient.invalidateQueries({ queryKey: adminQueries.all() }),
  })
}
