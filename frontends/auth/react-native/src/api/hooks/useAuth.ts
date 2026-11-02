/**
 * @AngelaMos | 2026
 * useAuth.ts
 */

import {
  type QueryClient,
  type UseMutationResult,
  type UseQueryResult,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'
import { router } from 'expo-router'
import {
  AUTH_ERROR_MESSAGES,
  AuthResponseError,
  isValidLogoutAllResponse,
  isValidMobileLoginResponse,
  isValidUserResponse,
  type LoginRequest,
  type LogoutAllResponse,
  type MobileLoginResponse,
  type PasswordChangeRequest,
  type UserResponse,
} from '@/api/types'
import {
  apiClient,
  getSessionVersion,
  QUERY_STRATEGIES,
  queryClientPersister,
  setAccessToken,
} from '@/core/api'
import { API_ENDPOINTS, QUERY_KEYS } from '@/core/config'
import { useAuthStore } from '@/core/lib'
import { SECURE_KEYS, secureStorage } from '@/core/storage'

export const authQueries = {
  all: () => QUERY_KEYS.AUTH.ALL,
  me: () => QUERY_KEYS.AUTH.ME(),
} as const

const fetchCurrentUser = async (): Promise<UserResponse> => {
  const response = await apiClient.get<unknown>(API_ENDPOINTS.AUTH.ME)
  const data: unknown = response.data

  if (!isValidUserResponse(data)) {
    throw new AuthResponseError(
      AUTH_ERROR_MESSAGES.INVALID_USER_RESPONSE,
      API_ENDPOINTS.AUTH.ME
    )
  }

  return data
}

export const useCurrentUser = (): UseQueryResult<UserResponse, Error> => {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  return useQuery({
    queryKey: authQueries.me(),
    queryFn: fetchCurrentUser,
    enabled: isAuthenticated,
    ...QUERY_STRATEGIES.auth,
  })
}

const performLogin = async (
  credentials: LoginRequest
): Promise<MobileLoginResponse> => {
  const formData = new URLSearchParams()
  formData.append('username', credentials.username)
  formData.append('password', credentials.password)

  const response = await apiClient.post<unknown>(
    API_ENDPOINTS.AUTH.LOGIN,
    formData,
    {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }
  )

  const data: unknown = response.data

  if (!isValidMobileLoginResponse(data)) {
    throw new AuthResponseError(
      AUTH_ERROR_MESSAGES.INVALID_LOGIN_RESPONSE,
      API_ENDPOINTS.AUTH.LOGIN
    )
  }

  return data
}

export const useLogin = (): UseMutationResult<
  MobileLoginResponse,
  Error,
  LoginRequest
> => {
  const queryClient = useQueryClient()
  const login = useAuthStore((s) => s.login)

  return useMutation({
    mutationFn: performLogin,
    onSuccess: async (data: MobileLoginResponse): Promise<void> => {
      setAccessToken(null)
      const sessionVersion = getSessionVersion()
      const saved = await secureStorage.setItem(
        SECURE_KEYS.REFRESH_TOKEN,
        data.refresh_token
      )
      if (sessionVersion !== getSessionVersion()) {
        throw new Error('Session changed while saving credentials')
      }
      if (!saved) throw new Error('Unable to save the session securely')
      setAccessToken(data.access_token)

      login(data.user)

      queryClient.setQueryData(authQueries.me(), data.user)
    },
  })
}

const performLogout = async (): Promise<void> => {
  const refreshToken = await secureStorage.getItem(SECURE_KEYS.REFRESH_TOKEN)
  if (refreshToken) {
    await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT, {
      refresh_token: refreshToken,
    })
  }
}

const clearLocalSession = async (
  queryClient: QueryClient,
  expectedVersion: number | undefined
): Promise<void> => {
  if (expectedVersion !== getSessionVersion()) return
  setAccessToken(null)
  const clearedVersion = getSessionVersion()
  useAuthStore.getState().logout()
  queryClient.clear()
  const [removed] = await Promise.all([
    secureStorage.deleteItem(SECURE_KEYS.REFRESH_TOKEN),
    queryClientPersister.removeClient(),
  ])
  if (clearedVersion !== getSessionVersion()) return
  router.replace('/(auth)/login')
  if (!removed) throw new Error('Unable to remove the saved session securely')
}

export const useLogout = (): UseMutationResult<void, Error, void, number> => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: performLogout,
    onMutate: getSessionVersion,
    onSettled: async (
      _data,
      _error,
      _variables,
      sessionVersion
    ): Promise<void> => {
      await clearLocalSession(queryClient, sessionVersion)
    },
  })
}

const performLogoutAll = async (): Promise<LogoutAllResponse> => {
  const response = await apiClient.post<unknown>(API_ENDPOINTS.AUTH.LOGOUT_ALL)
  const data: unknown = response.data

  if (!isValidLogoutAllResponse(data)) {
    throw new AuthResponseError(
      AUTH_ERROR_MESSAGES.INVALID_LOGOUT_RESPONSE,
      API_ENDPOINTS.AUTH.LOGOUT_ALL
    )
  }

  return data
}

export const useLogoutAll = (): UseMutationResult<
  LogoutAllResponse,
  Error,
  void,
  number
> => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: performLogoutAll,
    onMutate: getSessionVersion,
    onSuccess: async (_data, _variables, sessionVersion): Promise<void> => {
      await clearLocalSession(queryClient, sessionVersion)
    },
  })
}

const performPasswordChange = async (
  data: PasswordChangeRequest
): Promise<void> => {
  await apiClient.post(API_ENDPOINTS.AUTH.CHANGE_PASSWORD, data)
}

export const useChangePassword = (): UseMutationResult<
  void,
  Error,
  PasswordChangeRequest,
  number
> => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: performPasswordChange,
    onMutate: getSessionVersion,
    onSuccess: async (_data, _variables, sessionVersion): Promise<void> => {
      await clearLocalSession(queryClient, sessionVersion)
    },
  })
}
