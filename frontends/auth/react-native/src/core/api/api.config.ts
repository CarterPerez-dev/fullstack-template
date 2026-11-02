// ===================
// © AngelaMos | 2026
// api.config.ts
// ===================

import axios, {
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from 'axios'
import { API_ENDPOINTS, APP_CONFIG, HTTP_STATUS } from '@/core/config'
import { SECURE_KEYS, secureStorage } from '@/core/storage'
import { ApiError, ApiErrorCode, transformAxiosError } from './errors'

interface RequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
  _sessionVersion?: number
}

interface RefreshAttempt {
  sessionVersion: number
  promise: Promise<string>
}

interface RefreshResponse {
  access_token: string
  refresh_token: string
}

const getBaseURL = (): string => {
  const url = APP_CONFIG.API_URL
  if (!url || !/^https?:\/\//.test(url)) {
    throw new Error('Set EXPO_PUBLIC_API_URL to your backend URL')
  }
  if (!__DEV__ && !url.startsWith('https://')) {
    throw new Error('EXPO_PUBLIC_API_URL must use HTTPS in production')
  }
  return url.replace(/\/$/, '')
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: getBaseURL(),
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

let refreshAttempt: RefreshAttempt | null = null
let accessToken: string | null = null
let sessionVersion = 0

export const setAccessToken = (token: string | null): void => {
  sessionVersion += 1
  accessToken = token
}

export const getSessionVersion = (): number => sessionVersion

export const getAccessToken = (): string | null => {
  return accessToken
}

const assertCurrentSession = (version: number | undefined): void => {
  if (version !== sessionVersion) {
    throw new ApiError(
      'Session changed',
      ApiErrorCode.AUTHENTICATION_ERROR,
      HTTP_STATUS.UNAUTHORIZED
    )
  }
}

const handleTokenRefresh = async (version: number): Promise<string> => {
  const refreshToken = await secureStorage.getItem(SECURE_KEYS.REFRESH_TOKEN)
  assertCurrentSession(version)

  if (!refreshToken) {
    throw new ApiError(
      'No refresh token',
      ApiErrorCode.AUTHENTICATION_ERROR,
      HTTP_STATUS.UNAUTHORIZED
    )
  }

  const response = await apiClient.post<RefreshResponse>(
    API_ENDPOINTS.AUTH.REFRESH_MOBILE,
    { refresh_token: refreshToken }
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

  const { access_token, refresh_token: newRefreshToken } = response.data

  if (
    typeof access_token !== 'string' ||
    access_token.length === 0 ||
    typeof newRefreshToken !== 'string' ||
    newRefreshToken.length === 0
  ) {
    throw new ApiError(
      'Invalid refresh response tokens',
      ApiErrorCode.AUTHENTICATION_ERROR,
      HTTP_STATUS.UNAUTHORIZED
    )
  }

  assertCurrentSession(version)
  const saved = await secureStorage.setItem(
    SECURE_KEYS.REFRESH_TOKEN,
    newRefreshToken
  )
  assertCurrentSession(version)
  if (!saved) throw new Error('Unable to save the refreshed session securely')

  return access_token
}

let onAuthFailure: (() => void | Promise<void>) | null = null

export const setAuthFailureHandler = (
  handler: () => void | Promise<void>
): void => {
  onAuthFailure = handler
}

const handleAuthFailure = async (): Promise<void> => {
  setAccessToken(null)
  const [removed] = await Promise.all([
    secureStorage.deleteItem(SECURE_KEYS.REFRESH_TOKEN),
    onAuthFailure?.(),
  ])
  if (!removed) throw new Error('Unable to remove the saved session securely')
}

export const refreshAccessToken = (): Promise<string> => {
  const version = sessionVersion
  if (refreshAttempt?.sessionVersion === version) {
    return refreshAttempt.promise
  }
  const promise = handleTokenRefresh(version)
    .then((token) => {
      assertCurrentSession(version)
      accessToken = token
      return token
    })
    .catch(async (error: unknown) => {
      if (version === sessionVersion) await handleAuthFailure()
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
  refreshAttempt = { sessionVersion: version, promise }
  return promise
}

apiClient.interceptors.request.use(
  (config: RequestConfig): InternalAxiosRequestConfig => {
    config._sessionVersion ??= sessionVersion
    assertCurrentSession(config._sessionVersion)
    const token = getAccessToken()
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
    const isNotAuthEndpoint =
      !originalRequest.url?.includes('refresh') &&
      !originalRequest.url?.includes('login') &&
      !originalRequest.url?.includes('register') &&
      originalRequest.url !== API_ENDPOINTS.AUTH.LOGOUT

    if (isUnauthorized && isNotRetried && isNotAuthEndpoint) {
      originalRequest._retry = true
      const currentToken = getAccessToken()
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
