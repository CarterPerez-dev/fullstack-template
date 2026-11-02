// ===================
// © AngelaMos | 2025
// api.config.ts
// ===================

import axios, {
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from 'axios'
import { API_ENDPOINTS, HTTP_STATUS } from '@/config'
import { useAuthStore } from '@/core/lib'
import { ApiError, ApiErrorCode, transformAxiosError } from './errors'
import { decodeGoResponse } from './go-contract'

interface RequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
  _sessionVersion?: number
}

interface RefreshAttempt {
  sessionVersion: number
  promise: Promise<string>
}

const getBaseURL = (): string => {
  return import.meta.env.VITE_API_URL ?? '/api'
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: getBaseURL(),
  timeout: 15000,
  headers: { 'Content-Type': 'application/json', 'X-Auth-Transport': 'cookie' },
  withCredentials: true,
})

let refreshAttempt: RefreshAttempt | null = null

const assertCurrentSession = (version: number | undefined): void => {
  if (version !== useAuthStore.getState().sessionVersion) {
    throw new ApiError(
      'Session changed',
      ApiErrorCode.AUTHENTICATION_ERROR,
      HTTP_STATUS.UNAUTHORIZED
    )
  }
}

const handleTokenRefresh = async (): Promise<string> => {
  const response = await apiClient.post<{ access_token: string }>(
    API_ENDPOINTS.AUTH.REFRESH
  )

  if (
    response.data === null ||
    response.data === undefined ||
    typeof response.data !== 'object'
  ) {
    throw new ApiError(
      'Invalid refresh response',
      ApiErrorCode.AUTHENTICATION_ERROR,
      HTTP_STATUS.UNAUTHORIZED
    )
  }

  const accessToken = response.data.access_token
  if (typeof accessToken !== 'string' || accessToken.length === 0) {
    throw new ApiError(
      'Invalid access token',
      ApiErrorCode.AUTHENTICATION_ERROR,
      HTTP_STATUS.UNAUTHORIZED
    )
  }

  return accessToken
}

const handleAuthFailure = (): void => {
  useAuthStore.getState().logout()
  window.location.href = '/login'
}

export const refreshAccessToken = (): Promise<string> => {
  const { sessionVersion } = useAuthStore.getState()
  if (refreshAttempt?.sessionVersion === sessionVersion) {
    return refreshAttempt.promise
  }
  const promise = handleTokenRefresh()
    .then((token) => {
      assertCurrentSession(sessionVersion)
      useAuthStore.getState().setAccessToken(token)
      return token
    })
    .catch((error: unknown) => {
      if (sessionVersion === useAuthStore.getState().sessionVersion) {
        handleAuthFailure()
      }
      throw error instanceof ApiError
        ? error
        : new ApiError(
            'Session expired',
            ApiErrorCode.AUTHENTICATION_ERROR,
            HTTP_STATUS.UNAUTHORIZED
          )
    })
    .finally(() => {
      if (refreshAttempt?.promise === promise) refreshAttempt = null
    })
  refreshAttempt = { sessionVersion, promise }
  return promise
}

apiClient.interceptors.request.use(
  (config: RequestConfig): InternalAxiosRequestConfig => {
    const { accessToken: token, sessionVersion } = useAuthStore.getState()
    config._sessionVersion ??= sessionVersion
    assertCurrentSession(config._sessionVersion)
    if (token !== null && token.length > 0) {
      config.headers.Authorization = `Bearer ${token}`
    } else {
      config.headers.delete('Authorization')
    }
    return config
  },
  (error: unknown): Promise<never> => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response) => {
    assertCurrentSession((response.config as RequestConfig)._sessionVersion)
    if (response.status !== HTTP_STATUS.NO_CONTENT) {
      response.data = decodeGoResponse(response.data)
    }
    return response
  },
  async (error: AxiosError): Promise<unknown> => {
    if (error instanceof ApiError) return Promise.reject(error)
    const originalRequest = error.config as RequestConfig | undefined

    if (originalRequest === undefined) {
      return Promise.reject(transformAxiosError(error))
    }
    assertCurrentSession(originalRequest._sessionVersion)

    const isUnauthorized = error.response?.status === HTTP_STATUS.UNAUTHORIZED
    const isNotRetried = originalRequest._retry !== true
    const isNotRefreshEndpoint =
      originalRequest.url !== API_ENDPOINTS.AUTH.REFRESH &&
      originalRequest.url !== API_ENDPOINTS.AUTH.LOGOUT &&
      originalRequest.url !== API_ENDPOINTS.AUTH.LOGIN &&
      originalRequest.url !== API_ENDPOINTS.USERS.REGISTER

    if (isUnauthorized && isNotRetried && isNotRefreshEndpoint) {
      originalRequest._retry = true
      const currentToken = useAuthStore.getState().accessToken
      if (
        currentToken &&
        originalRequest.headers.Authorization !== `Bearer ${currentToken}`
      ) {
        originalRequest.headers.Authorization = `Bearer ${currentToken}`
        return apiClient(originalRequest)
      }
      const newToken = await refreshAccessToken()
      assertCurrentSession(originalRequest._sessionVersion)
      originalRequest.headers.Authorization = `Bearer ${newToken}`
      return apiClient(originalRequest)
    }

    return Promise.reject(transformAxiosError(error))
  }
)
