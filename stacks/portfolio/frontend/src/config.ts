// ===================
// © AngelaMos | 2026
// config.ts
// ===================
const API_VERSION = 'v1'

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: `/${API_VERSION}/auth/login`,
    REFRESH: `/${API_VERSION}/auth/refresh`,
    LOGOUT: `/${API_VERSION}/auth/logout`,
    LOGOUT_ALL: `/${API_VERSION}/auth/logout-all`,
    ME: `/${API_VERSION}/auth/me`,
    CHANGE_PASSWORD: `/${API_VERSION}/auth/change-password`,
  },
  USERS: {
    BASE: `/${API_VERSION}/users`,
    BY_ID: (id: string) => `/${API_VERSION}/users/${id}`,
    ME: `/${API_VERSION}/users/me`,
    REGISTER: `/${API_VERSION}/users`,
  },
  ADMIN: {
    USERS: {
      LIST: `/${API_VERSION}/admin/users`,
      CREATE: `/${API_VERSION}/admin/users`,
      BY_ID: (id: string) => `/${API_VERSION}/admin/users/${id}`,
      UPDATE: (id: string) => `/${API_VERSION}/admin/users/${id}`,
      DELETE: (id: string) => `/${API_VERSION}/admin/users/${id}`,
    },
  },
  PORTFOLIO: {
    PUBLIC: `/${API_VERSION}/portfolio`,
    REGISTRATION_STATUS: `/${API_VERSION}/portfolio/registration-status`,
    MEDIA_RAW: (id: string) => `/${API_VERSION}/media/${id}/raw`,
    PROFILE: `/${API_VERSION}/admin/portfolio/profile`,
    SETTINGS: `/${API_VERSION}/admin/portfolio/settings`,
    RESOURCE: (resource: string) => `/${API_VERSION}/admin/portfolio/${resource}`,
    RESOURCE_ITEM: (resource: string, id: string) =>
      `/${API_VERSION}/admin/portfolio/${resource}/${id}`,
    RESOURCE_REORDER: (resource: string) =>
      `/${API_VERSION}/admin/portfolio/${resource}/reorder`,
    MEDIA: `/${API_VERSION}/admin/portfolio/media`,
    MEDIA_ITEM: (id: string) => `/${API_VERSION}/admin/portfolio/media/${id}`,
  },
} as const

export const PORTFOLIO_RESOURCES = {
  CERTIFICATIONS: 'certifications',
  PROJECTS: 'projects',
  EXPERIENCE: 'experience',
  SKILL_GROUPS: 'skill-groups',
  LINKS: 'links',
  CUSTOM_SECTIONS: 'custom-sections',
} as const

const API_BASE = import.meta.env.VITE_API_URL ?? '/api'

export const mediaUrl = (id: string | null | undefined): string | null =>
  id === null || id === undefined || id.length === 0
    ? null
    : `${API_BASE}/${API_VERSION}/media/${id}/raw`

export const QUERY_KEYS = {
  AUTH: {
    ALL: ['auth'] as const,
    ME: () => [...QUERY_KEYS.AUTH.ALL, 'me'] as const,
  },
  USERS: {
    ALL: ['users'] as const,
    BY_ID: (id: string) => [...QUERY_KEYS.USERS.ALL, 'detail', id] as const,
    ME: () => [...QUERY_KEYS.USERS.ALL, 'me'] as const,
  },
  ADMIN: {
    ALL: ['admin'] as const,
    USERS: {
      ALL: () => [...QUERY_KEYS.ADMIN.ALL, 'users'] as const,
      LIST: (page: number, size: number) =>
        [...QUERY_KEYS.ADMIN.USERS.ALL(), 'list', { page, size }] as const,
      BY_ID: (id: string) =>
        [...QUERY_KEYS.ADMIN.USERS.ALL(), 'detail', id] as const,
    },
  },
  PORTFOLIO: {
    ALL: ['portfolio'] as const,
    PUBLIC: () => [...QUERY_KEYS.PORTFOLIO.ALL, 'public'] as const,
    REGISTRATION: () => [...QUERY_KEYS.PORTFOLIO.ALL, 'registration'] as const,
    RESOURCE: (resource: string) =>
      [...QUERY_KEYS.PORTFOLIO.ALL, resource] as const,
    MEDIA: () => [...QUERY_KEYS.PORTFOLIO.ALL, 'media'] as const,
  },
} as const

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  SETTINGS: '/settings',
  UNAUTHORIZED: '/unauthorized',
  ADMIN: {
    DASHBOARD: '/admin',
    USERS: '/admin/users',
    USER_DETAIL: (id: string) => `/admin/users/${id}`,
    PROFILE: '/admin/profile',
    APPEARANCE: '/admin/appearance',
    CERTIFICATIONS: '/admin/certifications',
    PROJECTS: '/admin/projects',
    EXPERIENCE: '/admin/experience',
    SKILLS: '/admin/skills',
    LINKS: '/admin/links',
    SECTIONS: '/admin/sections',
    MEDIA: '/admin/media',
  },
} as const

export const STORAGE_KEYS = {
  AUTH: 'auth-storage',
  UI: 'ui-storage',
} as const

export const QUERY_CONFIG = {
  STALE_TIME: {
    USER: 1000 * 60 * 5,
    STATIC: Infinity,
    FREQUENT: 1000 * 30,
  },
  GC_TIME: {
    DEFAULT: 1000 * 60 * 30,
    LONG: 1000 * 60 * 60,
  },
  RETRY: {
    DEFAULT: 3,
    NONE: 0,
  },
} as const

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER: 500,
} as const

export const PASSWORD_CONSTRAINTS = {
  MIN_LENGTH: 8,
  MAX_LENGTH: 128,
} as const

export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_SIZE: 20,
  MAX_SIZE: 100,
} as const

export type ApiEndpoint = typeof API_ENDPOINTS
export type QueryKey = typeof QUERY_KEYS
export type Route = typeof ROUTES
